from .chart_data_processing import *
import json
from .base_classes import ModuleBase
from threading import Thread
import subprocess, signal
import os

""" 

File containing Chart Controller and Simulator Module classes.
    
- Tuukka Varjus <tupevarj@student.jyu.fi> 
    
"""


class ChartController:
    """ Chart controller is responsible of pre-processing raw data for charts. """
    _data_name = ''
    _update_function = 0
    _tail = 0

    def __init__(self, data_name, update_func, tail=0):
        self._update_function = update_func
        self._data_name = data_name
        self._tail = tail

    def update(self, data_frame, context):
        """ Pre-processes raw data for chart. """
        if self._tail > 0:
            self._update_function(data_frame[self._data_name].tail(self._tail), context)
        else:
            self._update_function(data_frame[self._data_name], context)


class SimulatorModule(ModuleBase):
    """ Simulator module is responsible for running simulations and updating network
        performance charts. """
    chart_controllers = list()
    sim_thread = 0

    def __init__(self, mongo_connector):
        ModuleBase.__init__(self, mongo_connector=mongo_connector)
        """ Here is a list of all the chart controllers. 
            NOTE! MAGIC NUMBER IN REM_LOG (NUMBER OF PIXELS)!"""
        self.add_chart_controller(data_name='throughput_log', update_func=update_total_throughput_chart_data)
        self.add_chart_controller(data_name='main_kpis_log', update_func=update_rsrp_per_cell_chart_data)
        self.add_chart_controller(data_name='main_kpis_log', update_func=update_latest_rsrp_per_cell_chart_data)
        self.add_chart_controller(data_name='main_kpis_log', update_func=update_number_of_users_per_cell_chart_data)
        self.add_chart_controller(data_name='status_log', update_func=update_simulator_status_message_data)
        self.add_chart_controller(data_name='event_log', update_func=update_rlf_per_cell_chart_data)
        self.add_chart_controller(data_name='event_log', update_func=update_ac_cumulative_rlf_chart_data)
        self.add_chart_controller(data_name='rem_log', update_func=update_rem_map_chart, tail=22500)

        """ Here is a list of all the collection in DB needed in chart module. """
        self.add_mongo_collection_reader('throughput_log')
        self.add_mongo_collection_reader('main_kpis_log', primary=True)
        self.add_mongo_collection_reader('status_log')
        self.add_mongo_collection_reader('event_log')
        self.add_mongo_collection_reader('rem_log')

        """ Here is list of collection readers needed with outage creation/cancellation. 
            BE CAREFUL NOT TO CHANGE INDEXES. SHOULD BE IN DICTIONARY! """
        self.add_mongo_collection_writer(name='cell_configurations', values=[{"TxPower": -100.0}, {"TxPower": -100.0}, {"TxPower": -100.0}])
        self.add_mongo_collection_writer(name='cell_configurations', values=[{"TxPower": 43.0}, {"TxPower": 43.0}, {"TxPower": 43.0}])

    def initialize(self):
        """ Initialize method for simulator module. TODO: call initialize_data_processing. """
        return self.__update_charts()

    def add_chart_controller(self, data_name, update_func, tail=0):
        """ Adds chart controller with collecion name in mongo database <data_name>
            and function <update_func> to process data from that collection for chart. """
        self.chart_controllers.append(ChartController(data_name=data_name, update_func=update_func, tail=tail))

    def __check_if_initialized(self):
        for collection in self._mongo_collection_readers:
            if collection.primary and self._mongo_connector.check_initialized(collection):
                for collection in self._mongo_collection_readers:
                    collection.reset()
                initialize_data_processing()
                return True
        return False

    def __update_charts(self):
        """ First check if database has been intialized. After that, it reads new data from
            database and process that data into data understood by charts in the frontend. """
        response = dict()
        response['Initialize'] = json.dumps(self.__check_if_initialized())
        data = dict()
        for collection in self._mongo_collection_readers:
            data[collection.name] = self._mongo_connector.update_reader(collection)
        for chart_ctrl in self.chart_controllers:
            chart_ctrl.update(data, response)
        return response

    def __run_simulation(self, params):
        """ Launches script that starts ns-3 simulator with running option <params>"""
        subprocess.call(["./start_simulation.sh", params])

    def __start_simulation(self, training):
        """ Start ns-3 simulator either training or real simulation <training>. """
        if training:
            self.sim_thread = Thread(target=self.__run_simulation, args=("1",))
            self.sim_thread.start()
            return 'Training phase started.'
        else:
            self.sim_thread = Thread(target=self.__run_simulation, args=("0",))
            self.sim_thread.start()
            return 'Simulation started.'

    def __stop_simulation(self):
        """ Stops ns-3 from running by killing process. TODO: CLEAN THIS!! """
        dict_dfs = dict()
        if 0 < read_mongo_guaranteed(dictionary=dict_dfs, collection="simulation_configurations"):
            pid = dict_dfs["simulation_configurations"]["pid"][0]
            os.kill(pid, signal.SIGUSR2)
            self.sim_thread.join()
        return 'Simulation stopped.'

    def __outage_handler(self, params):
        """ Creates or cancels outage <params["CreateOutage"]> at basestation <params["BasestaionID"].
            Outage is created/cancelled by changing cell configurations in database """
        bs_id = int(params['BasestationID'])
        cells = basetation_to_cell_ids(bs_id)
        cell_info = str(bs_id) + " (Cells: " + str(cells[0]) + ', ' + str(cells[1]) + ' and ' + str(cells[2]) + ').'

        response = {'Message': "Outage cancelled at bs " + cell_info, 'status': 0}
        index = 1

        if int(params['CreateOutage']) != 0:    # Create outage
            index = 0
            response = {'Message': "Outage created at bs " + cell_info, 'status': 0}

        self._mongo_collection_writers[index].set_queries([{"CellID": cells[0]}, {"CellID": cells[1]}, {"CellID": cells[2]}])
        self._mongo_connector.update_writer(self._mongo_collection_writers[index])

        return response

    def __get_ue_location_history(self, params):
        """ Get user location and connection history request handler TODO: re-write this! """
        try:
            ue_id = int(params['UeID'])
        except ValueError:
            return 0
        return get_ue_location_and_connection_history(ue_id)

    def execute_command(self, command, params):
        """ Override of ModuleBase interface method. Execute commands
            based on path request <command> string. CHECK urls.py!

            Needs instance of Mongo module to get data needed for
            executing commands. """

        response_data = 0
        if command == '/updateCharts':
            response_data = self.__update_charts()
        elif command == '/startSimulation':
            response_data = self.__start_simulation(False)
        elif command == '/startTrainingSimulation':
            response_data = self.__start_simulation(True)
        elif command == '/stopSimulation':
            response_data = self.__stop_simulation()
        elif command == '/outageInput':
            response_data = self.__outage_handler(params)
        elif command == '/userLocationHistory':
            response_data = self.__get_ue_location_history(params)
        elif command == 'usersLocationHistoryCell':
            pass    # TODO: implement this!
        return response_data

