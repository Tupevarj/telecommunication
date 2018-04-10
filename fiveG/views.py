from django.shortcuts import render
from .models import read_collection_as_list_mongo, get_collection_count
from .models import collection_read_mongo, insert_document, \
    connect_to_mongo_db, is_database_unlocked, unlock_database, lock_database
import json
import numpy as np
from django.http import HttpResponse
from .data_processing import get_rsrp_per_cell_from_collection, calculate_total_throughput, \
    initialize_data_processing, preprocessed_data_to_csv_file, preprocess_training_set_to_8_and_10_dimensions,\
    preprocess_testing_set_to_10_dimensions
from .ml import run_ml, calculate_reference_z_scores, \
    train_and_test_all_regressions, save_all_regressors, load_all_regressors, Regressor, set_regressor, \
    get_reg_chart_data, get_reg_z_scores, get_auc_scores, get_current_z_scores
import time


# Global values
last_read_rsrp = 0
last_read_thr = 0
last_read_dominance = 0
last_read_ml = 0
training_ended = False  # cache

##############################################################
#   UPDATING CHARTS
##############################################################


def is_update_needed_for_alarm_table():
    """ Checks if there is new data in DB for ML algorithm """
    global last_read_ml
    count_map = get_collection_count(collection="main_kpis_log_labels")
    if last_read_ml == count_map:
        return False
    elif last_read_ml > count_map:    # DB dropped
        last_read_ml = 0
        return True
    else:
        return True


def is_update_needed_for_dominance_map():
    """ Checks if there is new data in DB for dominance map """
    global last_read_dominance
    count_map = get_collection_count(collection="dominationmap")
    if last_read_dominance == count_map:
        return False
    elif last_read_dominance > count_map:    # DB dropped
        last_read_dominance = 0
        return True
    else:
        return True


def is_update_needed_for_charts(context):
    """ Checks if there is new data in DB in main_kpis_log_labels or in throughput_log
        In addition checks if collection in DB has been dropped and based on that knowledge
        saves Initialize value to context """
    global last_read_rsrp
    global last_read_thr
    count_rsrp = get_collection_count(collection="main_kpis_log_labels")

    count_thr = get_collection_count(collection="throughput_log")
    if last_read_rsrp == count_rsrp and last_read_thr == count_thr:  # Not should need to use and
        context['Initialize'] = json.dumps(False)
        return False
    elif last_read_rsrp > count_rsrp and last_read_thr > count_thr:  # DB dropped
        last_read_rsrp = 0
        last_read_thr = 0
        initialize_data_processing()     # TODO: move elsewhere
        context['Initialize'] = json.dumps(True)
        return True
    else:
        context['Initialize'] = json.dumps(False)
        return True


def update_dominance_map(context):
    """ Updates dominance map: Save points (pixels) to context parameter """
    global last_read_dominance

    # Load dominance map from DB
    list_dominance = read_collection_as_list_mongo(collection="dominationmap", skip=last_read_dominance)
    last_read_dominance += len(list_dominance)

    # Load dominance map from DB
    dict_dominance = dict()
    dict_dominance["Points"] = list()

    list_dominance_II = list_dominance[-22500:]
    # Create dictionary from dominance map values:  TODO: Make this as separate function!
    for i in range(0, len(list_dominance_II)):    # FIXME: Hard coded pixel count!!!
        dict_dominance["Points"].append([int(round(list_dominance_II[i]['x'])), int(round(list_dominance_II[i]['y'])),
                                        10*np.log10(list_dominance_II[i]['sinr'])])
    context['DominanceMap'] = json.dumps(dict_dominance)


def create_context_for_reg_graphs():
    """ Creates context for regression charts"""
    context = dict()
    points = get_reg_chart_data()
    auc_scores = get_auc_scores()
    z_scores = get_reg_z_scores()

    context['Regression'] = json.dumps(points[Regressor.SIMPLE_REG.value])
    context['RegressionSVR'] = json.dumps(points[Regressor.SVR_REG.value])
    context['RegressionDT'] = json.dumps(points[Regressor.DECISION_TREE_REG.value])
    context['RegressionRF'] = json.dumps(points[Regressor.RANDOM_FOREST_REG.value])
    context['sRegAUC'] = json.dumps(auc_scores[Regressor.SIMPLE_REG.value])
    context['rfRegAUC'] = json.dumps(auc_scores[Regressor.RANDOM_FOREST_REG.value])
    context['svcRegAUC'] = json.dumps(auc_scores[Regressor.SVR_REG.value])
    context['dtRegAUC'] = json.dumps(auc_scores[Regressor.DECISION_TREE_REG.value])
    context['ZScores'] = json.dumps(z_scores[Regressor.SIMPLE_REG.value])
    return context


def update_charts_data(context):
    """" Adds data to context parameter for RSRPs and throughput charts """
    global last_read_rsrp
    global last_read_thr

    dict_rsrp_graph = dict()
    dict_rsrp_graph["Time"] = list()

    # RSRP: Load main_kpis log from DB
    list_main_kpis = read_collection_as_list_mongo(collection="main_kpis_log_labels", skip=last_read_rsrp)
    last_read_rsrp += len(list_main_kpis)

    # THROUGHPUT: Load throughput log from DB
    throughput_new = read_collection_as_list_mongo(collection="throughput_log", skip=last_read_thr)
    last_read_thr += len(throughput_new)

    # Create RSRP dictionary
    get_rsrp_per_cell_from_collection(list_rsrp=list_main_kpis, dict_rsrp=dict_rsrp_graph)

    # Calculate throughput
    throughput_result_new = dict()
    if len(throughput_new) > 0:
        throughput_result_new = calculate_total_throughput(throughput_new)

    # Get latest RSRP for each cell TODO: Make this as separate function!?!
    list_rsrp_per_cell = list()
    for i in range(1, len(dict_rsrp_graph)):
        list_rsrp_per_cell.append(dict_rsrp_graph["RSRP" + str(i)][-1])

    context['TotalThroughput'] = json.dumps(throughput_result_new)
    context['RSRP'] = json.dumps(dict_rsrp_graph)
    context['RsrpPerCell'] = list_rsrp_per_cell


##############################################################
#   END : UPDATING CHARTS
##############################################################


def create_regression_models():
    """ First preprocesses data from database and then trains regression
        models with it """
    while not is_database_unlocked(True):
        time.sleep(0.1)
    lock_database(True)
    data = collection_read_mongo(collection="main_kpis_log_labels")
    unlock_database(True)
    if len(data) > 0:
        array_8_dim = []
        labels = []
        array_10_dim = []
        preprocess_training_set_to_8_and_10_dimensions(dim_8_list=array_8_dim, dim_10_list=array_10_dim,
                                                       labels=labels, data_frame=data)
        train_and_test_all_regressions(array_8_dim, labels)
        calculate_reference_z_scores(array_x=array_10_dim, array_y=labels)


##############################################################
#   HTTP REQUEST HANDLERS
##############################################################


def update_charts(request):
    """ Main update routine for charts; checks if charts needs to be updated
        and returns data needed for charts """
    if request.method == "GET" and request.path == '/updateCharts':
        # Create context to be send to html file:
        context = dict()
        # Check if needs to be updated
        if is_database_unlocked(True):
            lock_database(True)
            if is_update_needed_for_charts(context):
                update_charts_data(context)
            if is_update_needed_for_dominance_map():
                update_dominance_map(context)
            unlock_database(True)
            return HttpResponse(json.dumps(context))
    return HttpResponse(json.dumps(0))


def select_reg_model(request):
    """" Set regression model and return references Z-scores accordingly selection """
    reg = int(request.GET['selectedReg'])
    set_regressor(reg)
    context = dict()
    z_scores = get_current_z_scores()
    context['ZScores'] = json.dumps(z_scores)
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


def update_alarm_gui(request):
    """ Run ML Algorithm and return data for alarm table
        and Z-Score chart """
    if request.method == "GET":
        global last_read_ml
        global training_ended
        if training_ended and is_update_needed_for_alarm_table():
            response_data = {'total': 1, 'rows': []}

            while not is_database_unlocked(True):
                time.sleep(0.01)

            lock_database(True)
            data = collection_read_mongo(collection="main_kpis_log_labels", skip=last_read_ml)
            unlock_database(True)
            last_read_ml += len(data)

            if len(data) > 0:
                array_10_dim = preprocess_testing_set_to_10_dimensions(data)
                ml_data = run_ml(array_10_dim)      # ML data has outage cell ID in first element and Z-scores in second element
                response_data['ZScores'] = json.dumps(ml_data[1])

                for i in range(1, 8):
                    severity = "Normal"
                    problem = "Normal Traffic"
                    if i == ml_data[0]:
                        severity = "Critical"
                        problem = "Outage"
                    response_data['rows'].append({"bsID": i, "created": "00.00.00", "severity": severity, "problem": problem, "service": "eUTRAN"})

                return HttpResponse(json.dumps(response_data))
        return HttpResponse(json.dumps(0))


def controlPanel(request):
    if request.method == "GET":
        if request.GET.get("cellID") == "":
            cellID = 0
        else:
            cellID = request.GET.get("cellID")

        if request.GET.get("normal") != None:
            normal = request.GET.get("normal")
        else:
            normal = 0

        if request.GET.get("outage") != None:
            outage = request.GET.get("outage")
        else:
            outage = 0

        if request.GET.get("coc") != None:
            coc = request.GET.get("coc")
        else:
            coc = 0

        if request.GET.get("cco") != None:
            cco = request.GET.get("cco")
        else:
            cco = 0

        if request.GET.get("mro") != None:
            mro = request.GET.get("mro")
        else:
            mro = 0

        if request.GET.get("mlb") != None:
            mlb = request.GET.get("mlb")
        else:
            mlb = 0

        document = {"cellID": int(cellID),
                    "normal": int(normal),
                    "outage": int(outage),
                    "coc": int(coc),
                    "cco": int(cco),
                    "mro": int(mro),
                    "mlb": int(mlb),
                    "dirty_flag": 0
                    }

        if cellID == 0:
            info = "Warning, the control Panel encounters problems, fixing"
            return HttpResponse(json.dumps(info))
        else:
            # store this operation into mongoDB collecton - control Panel
            # insert one document into database
            info = "Successfully finish new operation"
            while not is_database_unlocked(True):
                time.sleep(0.1)
            lock_database(False)
            insert_document("controlpanel", document)
            unlock_database(False)
            return HttpResponse(json.dumps(info))


##############################################################
#   END: HTTP REQUEST HANDLERS
##############################################################


def initialize():
    """ Initialize global values when page is refreshed """
    global last_read_rsrp
    global last_read_thr
    global last_read_dominance
    global ml_is_calculating
    global training_ended
    global last_read_ml
    last_read_ml = 0
    last_read_rsrp = 0
    last_read_thr = 0
    last_read_dominance = 0
    connect_to_mongo_db()
    ml_is_calculating = False
    training_ended = False


def index(request):
    """ ENTRY POINT
        Read data from mongoDB and preprocess data for graphs in front-end """
    # Initialize global values:
    initialize()
    initialize_data_processing()

    # Load data for charts:
    context = dict()

    while not is_database_unlocked(True):
        time.sleep(0.1)

    lock_database(True)
    update_charts_data(context)
    update_dominance_map(context)
    unlock_database(True)

    context['Regression'] = json.dumps([0, 0])  # TODO: Get rid of this
    context['RegressionSVR'] = json.dumps([0, 0])  # TODO: Get rid of this
    context['RegressionDT'] = json.dumps([0, 0])  # TODO: Get rid of this
    context['RegressionRF'] = json.dumps([0, 0])  # TODO: Get rid of this
    context['ZScores'] = json.dumps([0, 0, 0, 0, 0, 0, 0])  # TODO: Get rid of this

    return render(request, 'fiveG/index.html', context)
