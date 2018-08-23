from django.http import HttpResponse
from .chart_data_processing import *
from .mongo_module import CollectionReader
import json


class ChartController:
   # data = 0
    data_name = ''
    update_function = 0

    def __init__(self, data_name, update_func):
        self.update_function = update_func
        self.data_name = data_name

    def update(self, data_frame, context):
        self.update_function(data_frame[self.data_name], context)
        #self.data = \  OR RETURN DATA ONLY?


class ChartModule:
    """ Chart module is responsible for updating all the charts. """
    chart_controllers = list()
    mongo_collections = list()

    def __init__(self):
        """ Here is a list of all the chart controllers. """
        self.add_chart_controller(data_name='throughput_log', update_func=update_total_throughput_chart_data)
        self.add_chart_controller(data_name='main_kpis_log', update_func=update_rsrp_per_cell_chart_data)
        self.add_chart_controller(data_name='main_kpis_log', update_func=update_latest_rsrp_per_cell_chart_data)
        self.add_chart_controller(data_name='main_kpis_log', update_func=update_number_of_users_per_cell_chart_data)
        self.add_chart_controller(data_name='status_log', update_func=update_simulator_status_message_data)
        self.add_chart_controller(data_name='event_log', update_func=update_rlf_per_cell_chart_data)
        self.add_chart_controller(data_name='event_log', update_func=update_ac_cumulative_rlf_chart_data)
        self.add_chart_controller(data_name='rem_log', update_func=update_rem_map_chart)

        """ Here is a list of all the collection in DB needed in chart module. """
        self.add_mongo_collection('throughput_log')
        self.add_mongo_collection('main_kpis_log')
        self.add_mongo_collection('status_log')
        self.add_mongo_collection('event_log')
        self.add_mongo_collection('rem_log')        # TAIL?

    def add_chart_controller(self, data_name, update_func):
        self.chart_controllers.append(ChartController(data_name=data_name, update_func=update_func))

    def add_mongo_collection(self, name):
        self.mongo_collections.append(CollectionReader(name))

    def update(self, mongo_module, context):
        collections = dict()
        for collection in self.mongo_collections:
            collections[collection.name] = mongo_module.update_reader(collection)[collection.name]

        context['Initialize'] = json.dumps(False)   # TODO: FIX THIS!

        for chart_ctrl in self.chart_controllers:
            chart_ctrl.update(collections, context)
