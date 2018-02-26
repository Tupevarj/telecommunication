from django.shortcuts import render
from .models import collection_read_mongo, insert_document, calculate_dominatemap_size
import json
from django.core.paginator import Paginator
from django.http import HttpResponse
from .ml import calculateThroughput, displayDominateMap, detectUnnormalCell, calculateRSRP
import pandas as pd
#from PIL import Image
from django.conf import settings

# declare global variables

throughputCapacityData = collection_read_mongo(collection="main_file_with_UserTHR")
initialRecordNum = len(throughputCapacityData)
cursorLocation = len(throughputCapacityData)
oneTimeExtraRecord = 2280
dominateMap_size = 0
def index(request):

    # get main_file_with_UserThR collection from mongo
    global dominateMap_size

    throughput_Result = calculateThroughput(throughputCapacityData[:initialRecordNum])

    rsrp_Result = calculateRSRP(throughputCapacityData[:initialRecordNum])

    dominateMap_size = displayDominateMap()
    context = {
        "UserThroughput": throughput_Result,
        "rsrp": rsrp_Result
    }

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



def loadMore(request):
    global cursorLocation
    global oneTimeExtraRecord
    if request.method == "GET":
        nextCursorLocation = cursorLocation + oneTimeExtraRecord
        throughputCapacityData = collection_read_mongo(collection="main_file_with_UserTHR")
        thisResult = calculateThroughput(throughputCapacityData[cursorLocation:nextCursorLocation])

        # load more for cell RSRP graph
        rsrpLoadMoreResult = calculateRSRP(throughputCapacityData[cursorLocation:nextCursorLocation])
        result = {"throughputTime": thisResult["Time"],
                  "throughput": thisResult["throughput"],
                  "rsrpTime":rsrpLoadMoreResult["Time"],
                  "RSRP_1": rsrpLoadMoreResult["RSRP_1"],
                  "RSRP_2": rsrpLoadMoreResult["RSRP_2"],
                  "RSRP_3": rsrpLoadMoreResul




                  t["RSRP_3"]}
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




