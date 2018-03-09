from django.shortcuts import render
from .models import collection_read_mongo, insert_document, calculate_dominatemap_size, \
    read_collection_as_list_mongo, get_collection_count
from .models import collection_read_mongo, insert_document, calculate_dominatemap_size, \
    connect_to_mongo_db
import json
import numpy as np
from django.core.paginator import Paginator
from django.http import HttpResponse
from .ml import calculate_total_throughput, displayDominateMap, detectUnnormalCell, \
    get_rsrp_per_cell_from_collection_II, calculate_total_throughput_II, \
    initialize_ml, preprocessed_data_to_csv_file
import pandas as pd
#from PIL import Image
from django.conf import settings


# Global values
last_read_rsrp = 0
last_read_thr = 0
last_read_dominance = 0

##############################################################
#   UPDATING CHARTS
##############################################################


def is_update_needed_for_dominance_map():
    """ Checks if there is new data in DB for dominance map """
    global last_read_dominance
    count_map = get_collection_count(collection="dominationmap")
    if last_read_dominance >= count_map:
        return False
    else:
        return True


def is_update_needed_for_charts():
    """ Checks if there is new data in DB in main_kpis_log or in throughput_log """
    global last_read_rsrp
    global last_read_thr
    #check_and_average_buffer()
    count_rsrp = get_collection_count(collection="main_kpis_log")

    count_thr = get_collection_count(collection="throughput_log")
    if last_read_rsrp >= count_rsrp and last_read_thr >= count_thr: # Not should need to use and
        return False
    else:
        return True


def update_dominance_map(context):
    global last_read_dominance

    # Load d    ominance map from DB
    list_dominance = read_collection_as_list_mongo(collection="dominationmap", skip=last_read_dominance)
    last_read_dominance += len(list_dominance)

    # Load dominance map from DB
    dict_dominance = dict()
    dict_dominance["Points"] = list()

    # Create dictionary from dominance map values:  TODO: Make this as separate function!
    for i in range(0, len(list_dominance)):
        dict_dominance["Points"].append([int(round(list_dominance[i]['x'])), int(round(list_dominance[i]['y'])),
                                        10*np.log10(list_dominance[i]['sinr'])])

    context['DominanceMap'] = json.dumps(dict_dominance)


def update_charts_data(context):
    global last_read_rsrp
    global last_read_thr

    dict_rsrp_graph = dict()
    dict_rsrp_graph["Time"] = list()


    # RSRP: Load main_kpis log from DB
    list_main_kpis = read_collection_as_list_mongo(collection="main_kpis_log", skip=last_read_rsrp)
    last_read_rsrp += len(list_main_kpis)


    # THROUGHPUT: Load throughput log from DB
  #  list_thr = read_collection_as_list_mongo(collection="throughput_log", skip=last_read_thr)
  #  last_read_thr += len(list_thr)

    # THROUGHPUT: Load throughput log from DB
  # throughput_log_db = collection_read_mongo(collection="throughput_log")
    throughput_new = collection_read_mongo(collection="throughput_log", skip=last_read_thr)
    last_read_thr += len(throughput_new)

    #throughput_new = read_collection_as_list_mongo(collection="throughput_log", skip=last_read_thr)
    #last_read_thr += len(throughput_new)


    # Create RSRP dictionary
    get_rsrp_per_cell_from_collection_II(list_rsrp=list_main_kpis, dict_rsrp=dict_rsrp_graph)

    # Calculate throughput
    #if len(list_thr) > 0:
    #    list_thr = calculate_total_throughput_II(list_thr)
    #throughput_result = calculate_total_throughput(throughput_log_db[:len(throughput_log_db)])
    throughput_result_new = dict()
    if len(throughput_new) > 0:
      throughput_result_new = calculate_total_throughput(throughput_new[:len(throughput_new)])
      #throughput_result_new = calculate_total_throughput_II(throughput_new)


    #calculate_total_throughput_II


    # Get latest RSRP for each cell TODO: Make this as separate function!?!
    list_rsrp_per_cell = list()
    for i in range(1, len(dict_rsrp_graph)):
        list_rsrp_per_cell.append(dict_rsrp_graph["RSRP" + str(i)][-1])

    context['TotalThroughput'] = json.dumps(throughput_result_new)
    #context['TotalThroughput'] = json.dumps(list_thr)
    context['RSRP'] = json.dumps(dict_rsrp_graph)
    #context['ThrNew'] = json.dumps(throughput_result_new)
    context['RsrpPerCell'] = list_rsrp_per_cell


def update_charts(request):
    """ Main update routine for charts; checks if charts needs to be updated
        and returns data needed for charts. TODO: Should we only response if new data is available?
        (Currently we are doing unnecessary checks in front-end.)"""
    if request.method == "GET" and request.path == '/updateCharts':
        # Create context to be send to html file:
        context = dict()
        # Check if needs to be updated
        if is_update_needed_for_charts():
            update_charts_data(context)
        if is_update_needed_for_dominance_map():
            update_dominance_map(context)
        return HttpResponse(json.dumps(context))
    else:
        return 0


##############################################################
#   END : UPDATING CHARTS
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


def initialize():
    """ Initialize global values when page is refreshed """
    global last_read_rsrp
    global last_read_thr
    global last_read_dominance
    last_read_rsrp = 0
    last_read_thr = 0
    last_read_dominance = 0
    connect_to_mongo_db()
    #initialize_ml()


def index(request):
    """ ENTRY POINT
        Read data from mongoDB and preprocess data for graphs in front-end """
    # Initialize global values:
    initialize()

    # Load data for charts:
    context = dict()
    update_charts_data(context)
    update_dominance_map(context)

    return render(request, 'fiveG/index.html', context)


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

    print("enter this function, enter this function, enter this function")
    if request.method == "GET":
        print(request.GET)
        limit = request.GET.get('limit')  # how many items per page
        offset = request.GET.get('offset')  # how many items in total in the DB
        search = request.GET.get('search')
        sort_column = request.GET.get('sort')  # which column need to sort
        order = request.GET.get('order')  # ascending or descending
        if search:
            # all_records = collection_read_mongo(collection="event_log")
            all_records = detectUnnormalCell()
        else:
            # all_records = collection_read_mongo(collection="event_log")
            all_records = detectUnnormalCell()

        # all_records = all_records.insert(0, "order", range(0, len(all_records.index)))

        # all_records_count = len(all_records.index)
        all_records_count = 100
        if not offset:
            offset = 0
        if not limit:
            limit = 10

        all_records_list = all_records[:100].values.tolist()
        pageinator = Paginator(all_records_list, limit)

        page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_records_count, 'rows': []}

        for record in pageinator.page(page):
            print(record)

            response_data['rows'].append({
                "CellID": record[0] if record[0] else "",
                "Created": record[1] if record[1] else "",
                "Severity": record[3] if record[3] else "",
                "Problem Class": record[4] if record[4] else "",
                "Service Class": record[5] if record[5] else ""
            })

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
        main_kpis_log_db = collection_read_mongo(collection="main_kpis_log_labels ")
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
