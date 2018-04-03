from django.shortcuts import render
from .models import collection_read_mongo, insert_document, calculate_dominatemap_size, \
    read_collection_as_list_mongo, get_collection_count
from .models import collection_read_mongo, insert_document, calculate_dominatemap_size, \
    connect_to_mongo_db, is_database_unlocked, unlock_database, lock_database
import json
import numpy as np
from django.core.paginator import Paginator
from django.http import HttpResponse
from .ml import calculate_total_throughput, displayDominateMap, detectUnnormalCell, \
    get_rsrp_per_cell_from_collection_II, calculate_total_throughput_II, \
    initialize_ml, preprocess_data_8_dim, do_simple_regression, do_decision_tree_regression, \
    do_random_forest_regression, do_svr_regression, do_z_score_regression, preprocessed_data_to_csv_file, \
    preprocess_training_set, preprocess_training_set_8_dim
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
                roc_auc1 = [1]
                roc_auc2 = [1]
                roc_auc3 = [1]
                roc_auc4 = [1]

                array_x = []
                array_y = []
                array_x_II = []
                preprocess_training_set_8_dim(array_x=array_x, array_x_II=array_x_II, array_y=array_y, data_frame=data)
               # processed = preprocess_data_8_dim(data)
              #  preprocess_training_set(array_x, array_y, processed)

               # z_scores = do_z_score_regression(array_x=array_x_II, array_y=array_y, data=data)
                points1 = do_simple_regression(array_x, array_y, roc_auc1)
                points2 = do_svr_regression(array_x, array_y, roc_auc2)
                points3 = do_decision_tree_regression(array_x, array_y, roc_auc3)
                points4 = do_random_forest_regression(array_x, array_y, roc_auc4)

                context['Regression'] = json.dumps(points1)
                context['RegressionSVR'] = json.dumps(points2)
                context['RegressionDT'] = json.dumps(points3)
                context['RegressionRF'] = json.dumps(points4)
               # context['ZScores'] = json.dumps(z_scores)

                context['sRegAUC'] = json.dumps(roc_auc1[0])
                context['rfRegAUC'] = json.dumps(roc_auc4[0])
                context['svcRegAUC'] = json.dumps(roc_auc2[0])
                context['dtRegAUC'] = json.dumps(roc_auc3[0])
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


def updata_alarm_gui(request):
    if request.method == "GET":
        response_data = {'total': 1, 'rows': []}

        for i in range(1, 8):
            response_data['rows'].append({
                "bsID": i,
                "created": "TEST2",
                "severity": "TEST3",
                "problem": "TEST4",
                "service": "TEST5"})

        return HttpResponse(json.dumps(response_data))


##############################################################
#   NOT USED FUNCTIONS AND VARIABLES
##############################################################


# declare global variables
#throughputCapacityData = collection_read_mongo(collection="throughput_log")
#initialRecordNum = len(throughputCapacityData)
#cursorLocation = len(throughputCapacityData)
#oneTimeExtraRecord = 2280
#dominateMap_size = 0

# NOT USED ANYMORE - TUUKKA 9.3
def show_normal_col_in_table(request):
    global auck
    if request.method == "GET":
        # print(request.GET)
        # limit = request.GET.get('limit')  # how many items per page
        # offset = request.GET.get('offset')  # how many items in total in the DB
        # search = request.GET.get('search')
        # sort_column = request.GET.get('sort')  # which column need to sort
        # order = request.GET.get('order')  # ascending or descending
        # if search:
        #     # all_records = collection_read_mongo(collection="event_log")
        #     all_records = detectUnnormalCell()
        # else:
        #     # all_records = collection_read_mongo(collection="event_log")
        #     all_records = detectUnnormalCell()
        #
        # # all_records = all_records.insert(0, "order", range(0, len(all_records.index)))
        #
        # # all_records_count = len(all_records.index)
        # all_records_count = 100
        # if not offset:
        #     offset = 0
        # if not limit:
        #     limit = 10
        #
        # all_records_list = all_records[:100].values.tolist()
        # pageinator = Paginator(all_records_list, limit)
        #
        # page = int(int(offset) / int(limit) + 1)
        # response_data = {'total': all_records_count, 'rows': []}
        #
        # for record in pageinator.page(page):
        #     print(record)
        #
        #     response_data['rows'].append({
        #         "CellID": record[0] if record[0] else "",
        #         "Created": record[1] if record[1] else "",
        #         "Severity": record[3] if record[3] else "",
        #         "Problem Class": record[4] if record[4] else "",
        #         "Service Class": record[5] if record[5] else ""
        #     })

        response_data = {'total': 1, 'rows': []}

        response_data['rows'].append({
            "CellID": auck,
            "Created": "TEST2",
            "Severity": "TEST3",
            "Problem Class": "TEST4",
            "Service Class": "TEST5"})

        return HttpResponse(json.dumps(response_data))


# NOT USED ANYMORE - TUUKKA 9.3
def displayDemo(request):
    template_names = "fiveG/displayDemo.html"
    normalCol = normalCol_read_mongo()
    context = {}
    return render(request, template_names)


# NOT USED ANYMORE - TUUKKA 9.3
def loadNewestDominateMap(request):
    if request.method == "GET":
        global dominateMap_size
        latest_size = calculate_dominatemap_size()
        if latest_size > dominateMap_size:
            #     generate new dominate map and then send it to the front end
            displayDominateMap()
            # update the global variable
            dominateMap_size = latest_size
            try:
                # base_image = Image.open(settings.MEDIA_ROOT + "dominationMap.png")
                with open(settings.MEDIA_ROOT + "dominationMap.png", "rb") as f:
                    return HttpResponse(f.read(), content_type="image/png")
            except IOError:
                return HttpResponse('')
        else:
            return HttpResponse('')


# WE ARE NOT USING THIS ANYMORE - TUUKKA 22.2 TODO: Delete
def loadMore(request):
    global cursorLocation
    global oneTimeExtraRecord
    if request.method == "GET":
        nextCursorLocation = cursorLocation + oneTimeExtraRecord
        # Load throughput log from DB
        throughput_log_db = collection_read_mongo(collection="throughput_log")
        # Load main_kpis log from DB
        main_kpis_log_db = collection_read_mongo(collection="main_kpis_log_labels")
        # Calculate throughput based on data from DB
        throughput_result_dict = calculate_total_throughput(throughput_log_db[cursorLocation:nextCursorLocation])

        # load more for cell RSRP graph
        rsrp_result_dict = calculate_rsrp_per_cell(main_kpis_log_db[cursorLocation:nextCursorLocation])
        result = {"throughputTime": throughput_result_dict["time"],
                  "throughput": throughput_result_dict["throughput"],
                  "rsrpTime":rsrp_result_dict["Time"],
                  "RSRP_1": rsrp_result_dict["RSRP_1"],
                  "RSRP_2": rsrp_result_dict["RSRP_2"],
                  "RSRP_3": rsrp_result_dict["RSRP_3"]}
        cursorLocation = nextCursorLocation
        return HttpResponse(json.dumps(result))
    else:
        return 0


##############################################################
#   END: NOT USED FUNCTIONS AND VARIABLES
##############################################################
