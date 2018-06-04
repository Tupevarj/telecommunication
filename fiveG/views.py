from django.shortcuts import render
from .models import read_collection_as_list_mongo, get_collection_count
from .models import collection_read_mongo, insert_document, \
    connect_to_mongo_db, collection_update_with_set, collection_update_multiple_with_set
import json
from django.http import HttpResponse
from .data_processing import preprocess_training_set_to_8_and_10_dimensions,\
    preprocess_testing_set_to_10_dimensions
from .chart_data_processing import initialize_data_processing, get_data_for_all_charts, \
    get_ue_location_and_connection_history, get_cell_locations_II
from .ml import run_ml, calculate_reference_z_scores, \
    train_and_test_all_regressions, save_all_regressors, load_all_regressors, Regressor, set_regressor, \
    get_reg_chart_data, get_reg_z_scores, get_auc_scores, get_current_z_scores, update_nb_cell_lists
import subprocess, signal
import os
from threading import Thread

# Global values
last_read_ml = 0
training_ended = False  # cache
outage_rows = [0, 0, 0]
sim_thread = 0

##############################################################
#   UPDATING CHARTS
##############################################################


def is_update_needed_for_alarm_table():
    """ Checks if there is new data in DB for ML algorithm """
    global last_read_ml
    count_map = get_collection_count(collection="main_kpis_log")
    if last_read_ml == count_map:
        return False
    elif last_read_ml > count_map:    # DB dropped
        last_read_ml = 0
        return True
    else:
        return True


def create_context_for_reg_graphs():
    """ Creates context for regression charts"""
    context = dict()
    points = get_reg_chart_data()
    auc_scores = get_auc_scores()
    z_scores = get_reg_z_scores()

    context['Regression'] = points[Regressor.SIMPLE_REG.value]
    context['RegressionSVR'] = points[Regressor.SVR_REG.value]
    context['RegressionDT'] = points[Regressor.DECISION_TREE_REG.value]
    context['RegressionRF'] = points[Regressor.RANDOM_FOREST_REG.value]
    context['sRegAUC'] = json.dumps(auc_scores[Regressor.SIMPLE_REG.value])
    context['rfRegAUC'] = json.dumps(auc_scores[Regressor.RANDOM_FOREST_REG.value])
    context['svcRegAUC'] = json.dumps(auc_scores[Regressor.SVR_REG.value])
    context['dtRegAUC'] = json.dumps(auc_scores[Regressor.DECISION_TREE_REG.value])
    context['ZScores'] = z_scores[Regressor.SIMPLE_REG.value]
    return context


##############################################################
#   END : UPDATING CHARTS
##############################################################

def update_nb_cell_lists_in_db():
    """ Updates neighbour list for each cell in DB."""
    update_nb_cell_lists()


def create_regression_models():
    """ First preprocesses data from database and then trains regression
        models with it """
    update_nb_cell_lists_in_db()    # FIXME: CALLING FROM HERE FOR NOW ON
    data = collection_read_mongo(collection="main_kpis_log")
    if len(data) > 0:
        array_8_dim = []
        labels = []
        array_10_dim = []
        preprocess_training_set_to_8_and_10_dimensions(dim_8_list=array_8_dim, dim_10_list=array_10_dim,
                                                       labels=labels, data_frame=data)
        train_and_test_all_regressions(array_8_dim, labels)
        calculate_reference_z_scores(array_x=array_10_dim, array_y=labels)


def basetation_to_cell_ids(bs_id):
    """ Converts basestation ID to corresponding cell IDs """
    start = (bs_id - 1) * 3 + 1
    list_cells = list()
    for i in range(0, 3):
        list_cells.append((start + i))

    return list_cells


def apply_coc():
    global outage_rows
    if outage_rows[2] == 0:
        return {'message': "No outage detected.", 'status': 1}
    else:
        nb_cells = read_collection_as_list_mongo(collection="nb_cell_list")
        outage_cell_ids = basetation_to_cell_ids(4)
        compensated_cell_list = list()
        # Compensate:
        for cell in outage_cell_ids:
            for nb_list in nb_cells:
                if cell == nb_list['CellID']:
                    for nb_cell in nb_list['NbCellIDs']:
                        if nb_cell not in outage_cell_ids and nb_cell not in compensated_cell_list:
                            compensated_cell_list.append(nb_cell)

        for cell_id in compensated_cell_list:
            collection_update_with_set(collection="cell_configurations", query={"CellID": cell_id}, value={"TxPower": 49.0})
    return {'message': "Outage at basestation " + str(outage_rows[2]) + " detected. Compensation activated for cells " +
                       str(compensated_cell_list) + ".", 'status': 0}

##############################################################
#   HTTP REQUEST HANDLERS
##############################################################


def run_simulation(params):
    subprocess.call(["./start_simulation.sh", params])


def stop_simulation(request):
    """" Stops running simulation TODO: status code?"""
    if request.method == "GET" and request.path == '/stopSimulation':
        global sim_thread
        list_state = read_collection_as_list_mongo("simulation_configurations")
        pid = list_state[0]['pid']
        os.kill(pid, signal.SIGUSR2)
        sim_thread.join()
    return HttpResponse(json.dumps("Simulation stopped."))


def start_simulation(request):
    """" Starts running simulation TODO: status code?"""
    if request.method == "GET" and request.path == '/startSimulation':
        global sim_thread
        sim_thread = Thread(target=run_simulation, args=("0",))
        sim_thread.start()
    return HttpResponse(json.dumps("Simulation started."))


def start_training_simulation(request):
    """" Starts running training simulation TODO: status code?"""
    if request.method == "GET" and request.path == '/startTrainingSimulation':
        global sim_thread
        sim_thread = Thread(target=run_simulation, args=("1",))
        sim_thread.start()
    return HttpResponse(json.dumps("Training phase started."))


def outage_button_handler(request):
    if request.method == "GET" and request.path == '/outageInput':
        state = int(request.GET['CreateOutage'])
        bs_id = int(request.GET['BasestationID'])
        list_cells = basetation_to_cell_ids(bs_id)
        if state != 0:
            # Create outage
            collection_update_multiple_with_set(collection="cell_configurations", queries=[{"CellID": list_cells[0]},
                                                {"CellID": list_cells[1]}, {"CellID": list_cells[2]}], values=[
                                                {"TxPower": 0.0}, {"TxPower": 0.0}, {"TxPower": 0.0}])
            return HttpResponse(json.dumps({'Message': "Outage created at bs " + str(bs_id) + " (Cells: " +
                                                       str(list_cells[0]) + ', ' + str(list_cells[1]) + ' and ' +
                                                       str(list_cells[2]) + ').', 'status': 0}))
        else:
            # Cancel outage
            collection_update_multiple_with_set(collection="cell_configurations", queries=[{"CellID": list_cells[0]},
                                                {"CellID": list_cells[1]}, {"CellID": list_cells[2]}], values=[
                                                {"TxPower": 46.0}, {"TxPower": 46.0}, {"TxPower": 46.0}])
            return HttpResponse(json.dumps({'Message': "Outage cancelled at bs " + str(bs_id) + " (Cells: " +
                                                       str(list_cells[0]) + ', ' + str(list_cells[1]) + ' and ' +
                                                       str(list_cells[2]) + ').', 'status': 0}))


def control_panel_input(request):
    if request.method == "GET" and request.path == '/controlPanelInput':
        event_id = int(request.GET['eventId'])
        if event_id == 0:
            try:
                bs_id_int = int(request.GET['bsId'])
            except ValueError:
                return HttpResponse(json.dumps({'message': "Please enter correct basestation ID.", 'status': 1}))
            if 0 < bs_id_int < 8:
                # Create outge TODO: change the way its created
                document = {"cellID": bs_id_int, "normal": 0, "outage": 1, "coc": 0,
                           "cco": 0, "mro": 0, "mlb": 0, "dirty_flag": 0 }
                insert_document("controlpanel", document)
                return HttpResponse(json.dumps({'message': "Outage created at basestation " + str(bs_id_int) + ".",
                                                'status': 0}))
            else:
                return HttpResponse(json.dumps({'message': "Please enter basestation ID from 1 to 7.", 'status': 1}))
        elif event_id == 1:
            message = apply_coc()
            return HttpResponse(json.dumps(message))
    return HttpResponse(json.dumps(0))


def update_charts(request):
    """ Main update routine for charts; checks if charts needs to be updated
        and returns data needed for charts """
    if request.method == "GET" and request.path == '/updateCharts':
        context = dict()
        get_data_for_all_charts(context)
        return HttpResponse(json.dumps(context))
    return HttpResponse(json.dumps(0))


def select_reg_model(request):
    """" Set regression model and return references Z-scores accordingly selection """
    reg = int(request.GET['selectedReg'])
    set_regressor(reg)
    context = dict()
    z_scores = get_current_z_scores()
    context['ZScores'] = z_scores
    return HttpResponse(json.dumps(context))


def load_ml_models(request):
    """ Load Regression models and data for regression charts from hard drive """
    global training_ended
    if request.method == "GET" and request.path == '/loadMLModels':
        if load_all_regressors() == 0:
            return HttpResponse(json.dumps(0))
        else:
            training_ended = True
            return HttpResponse(json.dumps(create_context_for_reg_graphs()))


def save_ml_models(request):
    """ Saves regression models to hard disk"""
    global training_ended
    if request.method == "GET" and request.path == '/saveMLModels':
        if training_ended:
            return HttpResponse(save_all_regressors())
        else:
            HttpResponse(0)


def create_ml_models(request):
    """ Fits Regression models and creates data for regression charts and table """
    global training_ended
    if request.method == "GET" and request.path == '/createModels':
        create_regression_models()
        training_ended = True
        return HttpResponse(json.dumps(create_context_for_reg_graphs()))
    else:
        return 0


def get_ue_location_history(request):
    """ Get user location and connection history request handler """
    if request.method == "GET":
        try:
            ue_id = int(request.GET['UeID'])
        except ValueError:
            return 0
        connections = get_ue_location_and_connection_history(int(ue_id))
        return HttpResponse(json.dumps(connections))
    else:
        return 0


def update_alarm_gui(request):
    """ Run ML Algorithm and return data for alarm table
        and Z-Score chart """
    if request.method == "GET":
        global last_read_ml
        global training_ended
        global outage_rows
        if training_ended and is_update_needed_for_alarm_table():
            response_data = {'total': 1, 'rows': []}
            data = collection_read_mongo(collection="main_kpis_log", skip=last_read_ml)
            last_read_ml += len(data)

            if len(data) != 0:
                array_10_dim = preprocess_testing_set_to_10_dimensions(data)
                ml_data = run_ml(array_10_dim)      # ML data has outage cell ID in first element and Z-scores in second element
                response_data['ZScores'] = ml_data[1]

                outage_id = ml_data[0]

                if outage_rows[0] == outage_id:
                    outage_rows[1] += 1
                else:
                    outage_rows[1] = 0
                if outage_rows[1] >= 5:  # outage_rows[1] >= 3 is not working with BS 3
                    outage_rows[2] = outage_id
                #    training_ended = False        # to stop after making a prediction

                outage_rows[0] = outage_id
                outage_id = outage_rows[2]

                for i in range(1, 8):
                    severity = "Normal"
                    problem = "Normal Traffic"
                    if i == outage_id:
                        severity = "Critical"
                        problem = "Outage"
                    response_data['rows'].append({"bsID": i, "created": "00.00.00", "severity": severity, "problem": problem, "service": "eUTRAN"})

                return HttpResponse(json.dumps(response_data))
        return HttpResponse(json.dumps(0))


##############################################################
#   END: HTTP REQUEST HANDLERS
##############################################################


def initialize():
    """ Initialize global values when page is refreshed """
    global ml_is_calculating
    global training_ended
    global last_read_ml
    global outage_rows
    last_read_ml = 0
    connect_to_mongo_db()
    ml_is_calculating = False
    training_ended = False
    outage_rows = [0, 0, 0]


def index(request):
    """ ENTRY POINT
        Read data from mongoDB and preprocess data for graphs in front-end """
    # Initialize global values:
    initialize()
    initialize_data_processing()
    # Load data for charts:
    context = dict()
    cell_locations = get_cell_locations_II()
    context['CellLocations'] = cell_locations
    get_data_for_all_charts(context)

    z_scores_chart = dict()
    z_scores_chart['BS'] = ["BS1", "BS2", "BS3", "BS4", "BS5", "BS6", "BS7" ]
    z_scores_chart['Ref. Z-scores'] = [0, 0, 0, 0, 0, 0, 0]
    z_scores_chart['Z Score'] = [0, 0, 0, 0, 0, 0, 0]
    context['ZScores'] = z_scores_chart  # TODO: Get rid of this

    return render(request, 'fiveG/index.html', context)
