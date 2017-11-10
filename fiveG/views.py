from django.shortcuts import render
from .models import normalCol_read_mongo
import json

# Create your views here.

def index(request):
    normalCol = normalCol_read_mongo()
    oneExample = normalCol[:1]
    print(normalCol[:1])
    x = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    normalColList = list(normalCol.values.flatten())
    data = {
        "Time": normalCol.iloc[0]["Time"],
        "UeNodeNo": normalCol.iloc[0]["UeNodeNo"],
        "UeRNTI": normalCol.iloc[0]["UeRNTI"],
        "Cell_ID": normalCol.iloc[0]["Cell_ID"],
        "RSRP": normalCol.iloc[0]["RSRP"],
        "RSRQ": normalCol.iloc[0]["RSRQ"],
        "Serving_Cell": normalCol.iloc[0]["Serving_Cell"]
    }
    context = {
        "item": data,
        "test": "testtest"
    }
    return render(request, 'fiveG/index.html', context)
    


def displayDemo(request):


    template_names = "displayDemo.html"

    normalCol = normalCol_read_mongo()


    context = {}
    print(template_names[:1])

    return render(request, template_names, context)