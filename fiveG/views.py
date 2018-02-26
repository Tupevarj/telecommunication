from django.shortcuts import render
from .models import collection_read_mongo, insert_document, calculate_dominatemap_size, \
    read_collection_as_list_mongo, get_collection_count
from .models import collection_read_mongo, insert_document, calculate_dominatemap_size
import json
import numpy as np
from django.core.paginator import Paginator
from django.http import HttpResponse
from .ml import calculate_total_throughput, displayDominateMap, detectUnnormalCell, \
    get_rsrp_per_cell_from_collection_II
import pandas as pd
#from PIL import Image
from django.conf import settings

# declare global variables

throughputCapacityData = collection_read_mongo(collection="throughput_log")
initialRecordNum = len(throughputCapacityData)
cursorLocation = len(throughputCapacityData)
oneTimeExtraRecord = 2280
dominateMap_size = 0

# Global values
last_read_rsrp = 0
last_read_thr = 0
last_read_dominance = 0
dict_rsrp_graph = dict()
dict_thr_graph = dict()


# #
# #   SET LIMIT VALUE FOR BUFFER
# #   - WHEN ITS DOUBLE THE BUFFER SIZE -> AVERAGE
# #
# #
# def average_rsrp_list(dict_rsrp_graph):
#     dict_averaged = dict()
#     dict_averaged["Time"] = list()
#     # CORRECT THE TIME
#     list_time = dict_rsrp_graph["Time"]
#     for i in range(1, (len(list_time) - 1), 2):
#         dict_averaged["Time"].append(list_time[i])
#
#     for cell in range(1, len(dict_rsrp_graph)):
#         key = "RSRP" + str(cell)
#         list_rsrp = dict_rsrp_graph[key]
#         dict_averaged[key] = list()
#         previous = list_rsrp[0]
#         for i in range(1, (len(list_rsrp) - 1), 2):
#             averaged = (previous + list_rsrp[i]) / 2.0
#             previous = list_rsrp[i+1]
#             dict_averaged[key].append(averaged)
#     return dict_averaged
#
#
# def check_and_average_buffer():
#     global dict_rsrp_graph
#     # CORRECT THE TIME
#
#     if len(dict_rsrp_graph["Time"]) > 30:
#         dict_rsrp_graph = dict(average_rsrp_list(dict_rsrp_graph))

def is_update_needed_for_dominance_map():
    global last_read_dominance
    count_map = get_collection_count(collection="dominationmap")
    if last_read_dominance >= count_map:
        return False
    else:
        return True


def is_update_needed_for_charts():
    global last_read_rsrp
    global last_read_thr
    #check_and_average_buffer()
    count_rsrp = get_collection_count(collection="main_kpis_log")
    count_thr = get_collection_count(collection="throughput_log")
    if last_read_rsrp >= count_rsrp and last_read_thr >= count_thr: # Not should need to use and
        return False
    else:
        return True


def initialize():
    global last_read_rsrp
    global last_read_thr
    global dict_rsrp_graph
    global dict_thr_graph
    last_read_rsrp = 0
    last_read_thr = 0
    dict_rsrp_graph.clear()
    dict_thr_graph.clear()
    dict_rsrp_graph["Time"] = list()  # WILL WE DO THIS IF LIST IS EMPTY??


def update_dominance_map(context):
    global last_read_dominance

    # Load dominance map from DB
    list_dominance = read_collection_as_list_mongo(collection="dominationmap", skip=last_read_dominance)
    last_read_dominance += len(list_dominance)

    # Load dominance map from DB
    dict_dominance = dict()
    dict_dominance["X"] = list()
    dict_dominance["Y"] = list()
    dict_dominance["Sinr"] = list()
    dict_dominance["Points"] = list()

    # Create dictionary from dominance map values:  TODO: Make this as separate function!
    for i in range(0, len(list_dominance)):
        dict_dominance["Points"].append([list_dominance[i]['x'], list_dominance[i]['y'],
                                        10*np.log10(list_dominance[i]['sinr'])])

    context['DominanceMap'] = json.dumps(dict_dominance)


def update_charts_data(context):
    global last_read_rsrp
    global last_read_thr
    global dict_rsrp_graph
    global dict_thr_graph
    # Load main_kpis log from DB
    list_main_kpis = read_collection_as_list_mongo(collection="main_kpis_log", skip=last_read_rsrp)
    last_read_rsrp += len(list_main_kpis)
    # Load throughput log from DB
    throughput_log_db = collection_read_mongo(collection="throughput_log")
    throughput_new = collection_read_mongo(collection="throughput_log", skip=last_read_thr)
    last_read_thr += len(throughput_log_db)
    # Create RSRP dictionary
    get_rsrp_per_cell_from_collection_II(list_rsrp=list_main_kpis, dict_rsrp=dict_rsrp_graph)

    # Calculate throughput
    throughput_result = calculate_total_throughput(throughput_log_db[:len(throughput_log_db)])
    throughput_result_new = dict()
    if len(throughput_new) > 0:
        throughput_result_new = calculate_total_throughput(throughput_new[:len(throughput_new)])

    # Get latest RSRP for each cell TODO: Make this as separate function!
    list_rsrp_per_cell = list()
    for i in range(1, len(dict_rsrp_graph)):
        list_rsrp_per_cell.append(dict_rsrp_graph["RSRP" + str(i)][-1])

    context['TotalThroughput'] = json.dumps(throughput_result)
    context['RSRP'] = json.dumps(dict_rsrp_graph)
    context['ThrNew'] = json.dumps(throughput_result_new)
    context['RsrpPerCell'] = list_rsrp_per_cell


def index(request):
    """ Read data from mongoDB and based on that data produce values for graphs
        in front-end. """
    # Get main_file_with_UserThR collection from mongo
    global dominateMap_size
    initialize()

    # Create context to be send to html file:
    context = dict()

    update_charts_data(context)
    update_dominance_map(context)

    return render(request, 'fiveG/index.html', context)


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



def update_charts(request):
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


def loadMore(request):
    global cursorLocation
    global oneTimeExtraRecord
    if request.method == "GET":
        nextCursorLocation = cursorLocation + oneTimeExtraRecord
        # Load throughput log from DB
        throughput_log_db = collection_read_mongo(collection="throughput_log")
        # Load main_kpis log from DB
        main_kpis_log_db = collection_read_mongo(collection="main_kpis_log ")
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




