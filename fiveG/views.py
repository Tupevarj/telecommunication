from django.shortcuts import render
from .models import collection_read_mongo, insert_document, calculate_dominatemap_size, \
    read_collection_as_list_mongo, get_collection_count
from .models import collection_read_mongo, insert_document, calculate_dominatemap_size, \
    connect_to_mongo_db, is_database_unlocked, unlock_database, lock_database
import json
import numpy as np
from django.core.paginator import Paginator
from django.http import HttpResponse
from .ml import calculate_total_throughput, \
    get_rsrp_per_cell_from_collection_II, calculate_total_throughput_II, \
    initialize_ml, run_ml, do_calculate_z_scores, preprocessed_data_to_csv_file, \
    preprocess_training_set_to_8_and_10_dimensions, do_all_regressions
import pandas as pd
#from PIL import Image
from django.conf import settings
import time


# Global values
last_read_rsrp = 0
last_read_thr = 0
last_read_dominance = 0
last_read_regression = 0
ml_is_calculating = False
training_ended = False  # cache

##############################################################
#   UPDATING CHARTS
##############################################################


def check_if_training_ended():
    return True
    global training_ended
    if training_ended:
        return True
    if is_database_unlocked(True):
        lock_database(True)
        data = collection_read_mongo(collection="main_kpis_log_labels")
        unlock_database(True)
        if data["Time"].iloc[-1] > 2.0:  # TODO: Check this magic number
            training_ended = True
            return True
    return False


def is_update_needed_for_regression_chart():
    global last_read_regression
    count_main_kpis = get_collection_count(collection="main_kpis_log_labels")
    if last_read_regression >= count_main_kpis:
        return False
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
        initialize_ml()     # TODO: move elsewhere
        context['Initialize'] = json.dumps(True)
        return True
    else:
        context['Initialize'] = json.dumps(False)
        return True


def update_dominance_map(context):
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


def update_regression_chart(context):
    global last_read_regression
    global ml_is_calculating
    if not ml_is_calculating and is_update_needed_for_regression_chart():  # and check_if_training_ended():
        if is_database_unlocked(True):
            lock_database(True)
            ml_is_calculating = True
            data = collection_read_mongo(collection="main_kpis_log_labels")
            unlock_database(True)
            last_read_regression = len(data)
            if len(data) > 0:

                array_8_dim = []
                labels = []
                array_10_dim = []
                preprocess_training_set_to_8_and_10_dimensions(dim_8_list=array_8_dim, dim_10_list=array_10_dim,
                                                               labels=labels, data_frame=data)

                auc_scores = dict()
                points = do_all_regressions(array_8_dim, labels, auc_scores)
                z_scores = do_calculate_z_scores(array_x=array_10_dim, array_y=labels)

                context['Regression'] = json.dumps(list(points[0]))
                context['RegressionSVR'] = json.dumps(list(points[3]))
                context['RegressionDT'] = json.dumps(list(points[1]))
                context['RegressionRF'] = json.dumps(list(points[2]))
                context['ZScores'] = json.dumps(z_scores)

                context['sRegAUC'] = json.dumps(auc_scores["simple"])
                context['rfRegAUC'] = json.dumps(auc_scores["rf"])
                context['svcRegAUC'] = json.dumps(auc_scores["svr"])
                context['dtRegAUC'] = json.dumps(auc_scores["dt"])
            ml_is_calculating = False


def update_charts_data(context):
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
    get_rsrp_per_cell_from_collection_II(list_rsrp=list_main_kpis, dict_rsrp=dict_rsrp_graph)

    # Calculate throughput
    throughput_result_new = dict()
    if len(throughput_new) > 0:
        throughput_result_new = calculate_total_throughput_II(throughput_new)

    # Get latest RSRP for each cell TODO: Make this as separate function!?!
    list_rsrp_per_cell = list()
    for i in range(1, len(dict_rsrp_graph)):
        list_rsrp_per_cell.append(dict_rsrp_graph["RSRP" + str(i)][-1])

    context['TotalThroughput'] = json.dumps(throughput_result_new)
    context['RSRP'] = json.dumps(dict_rsrp_graph)
    context['RsrpPerCell'] = list_rsrp_per_cell


def update_reg_chart(request):
    if request.method == "GET" and request.path == '/updateRegressionChart':
        context = dict()
        update_regression_chart(context)
        return HttpResponse(json.dumps(context))
    else:
        return 0


def update_charts(request):
    """ Main update routine for charts; checks if charts needs to be updated
        and returns data needed for charts. TODO: Should we only response if new data is available?
        (Currently we are doing unnecessary checks in front-end.)"""
    if request.method == "GET" and request.path == '/updateCharts':
        # Create context to be send to html file:
        context = dict()
        # Check if needs to be updated
        if is_database_unlocked(True):
            # TODO: USE THIS: time.sleep ??
            lock_database(True)
            if is_update_needed_for_charts(context):
                update_charts_data(context)
            if is_update_needed_for_dominance_map():
                update_dominance_map(context)
            unlock_database(True)
            return HttpResponse(json.dumps(context))
        return 0
    else:
        return 0


##############################################################
#   END : UPDATING CHARTS
##############################################################

##############################################################
#   UPDATE TABLE
##############################################################

def update_ml_table(request):
    global auck
    if request.method == "GET":
        response_data = {'total': 1, 'rows': []}
        response_data['rows'].append({"algorithm": "k-NNAD", "score": auck})
        response_data['rows'].append({"algorithm": "Algorithm2", "score": auck})

        return HttpResponse(json.dumps(response_data))


##############################################################
#   END : UPDATE TABLE
##############################################################

##############################################################
#   CONTROL PANEL
##############################################################

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
            info = "successfully finish new operation"
            insert_document("controlpanel", document)
            return HttpResponse(json.dumps(info))


##############################################################
#   END : CONTROL PANEL
##############################################################

def initialize():
    """ Initialize global values when page is refreshed """
    global last_read_rsrp
    global last_read_thr
    global last_read_dominance
    global last_read_regression
    global ml_is_calculating
    global training_ended
    last_read_rsrp = 0
    last_read_thr = 0
    last_read_dominance = 0
    last_read_regression = 0
    connect_to_mongo_db()
    ml_is_calculating = False
    training_ended = False


def index(request):
    """ ENTRY POINT
        Read data from mongoDB and preprocess data for graphs in front-end """
    # Initialize global values:
    initialize()
    initialize_ml()
    global auck

    # Load data for charts:
    context = dict()

    while not is_database_unlocked(True):
        time.sleep(0.1)

    lock_database(True)
    #preprocessed_data_to_csv_file("/home/tupevarj/NS3SimulatorData/realphase/")
    update_charts_data(context)
    update_dominance_map(context)
    unlock_database(True)

    #context["knAUC"] = json.dumps(auck)
    context['Regression'] = json.dumps([0, 0])  # TODO: Get rid of this
    context['RegressionSVR'] = json.dumps([0, 0])  # TODO: Get rid of this
    context['RegressionDT'] = json.dumps([0, 0])  # TODO: Get rid of this
    context['RegressionRF'] = json.dumps([0, 0])  # TODO: Get rid of this
    context['ZScores'] = json.dumps([0, 0, 0, 0, 0, 0, 0])  # TODO: Get rid of this

    return render(request, 'fiveG/index.html', context)


def update_alarm_gui(request):
    if request.method == "GET":
        response_data = {'total': 1, 'rows': []}

        lock_database(True)
        data = collection_read_mongo(collection="main_kpis_log_labels")
        unlock_database(True)

        array_8_dim = []
        labels = []
        array_10_dim = []
        preprocess_training_set_to_8_and_10_dimensions(dim_8_list=array_8_dim, dim_10_list=array_10_dim,
                                                       labels=labels, data_frame=data)
        outage_id = run_ml(array_10_dim)

        for i in range(1, 8):
            severity = "Normal"
            if i == outage_id:
                severity = "Critical"
            response_data['rows'].append({
                "bsID": i,
                "created": "TEST2",
                "severity": severity,
                "problem": "TEST4",
                "service": "TEST5"})

        return HttpResponse(json.dumps(response_data))


##############################################################
#   NOT USED FUNCTIONS AND VARIABLES
##############################################################



##############################################################
#   END: NOT USED FUNCTIONS AND VARIABLES
##############################################################
