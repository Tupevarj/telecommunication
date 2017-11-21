from django.shortcuts import render
from .models import normalCol_read_mongo, collection_read_mongo
import json
from django.core.paginator import Paginator
from django.http import HttpResponse
from .ml import calculateThroughput

# Create your views here.

def index(request):

    # get main_file_with_UserThR collection from mongo
    throughputCapacityData = collection_read_mongo(collection="main_file_with_UserTHR")
    result = calculateThroughput(throughputCapacityData[:200000])

    context = {
        "UserThroughput": result
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
            all_records = collection_read_mongo(collection="event_log")
            # all_records = normalCol_read_mongo()
        else:
            all_records = collection_read_mongo(collection="event_log")

        # all_records = all_records.insert(0, "order", range(0, len(all_records.index)))

        # all_records_count = len(all_records.index)
        all_records_count = 100
        if not offset:
            offset = 0
        if not limit:
            limit = 20

        all_records_list = all_records[:100].values.tolist()
        pageinator = Paginator(all_records_list, limit)

        page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_records_count, 'rows': []}

        for record in pageinator.page(page):
            print(record)

            response_data['rows'].append({
                "time": record[0] if record[0] else "",
                "X": record[1] if record[1] else "",
                "Y": record[2] if record[2] else "",
                "IMSI": record[3] if record[3] else "",
                "EVENT": record[4] if record[4] else "",
                "RSRQ": record[5] if record[5] else "",
                "CellID": record[6] if record[6] else ""
            })

        return HttpResponse(json.dumps(response_data))


def displayDemo(request):


    template_names = "fiveG/displayDemo.html"

    normalCol = normalCol_read_mongo()


    context = {}
    # print(template_names[:1])

    return render(request, template_names)