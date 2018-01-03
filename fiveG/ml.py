'''
this file deals with data analysis
'''
import django
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from .models import normalCol_read_mongo, collection_read_mongo, insert_document
from scipy.interpolate import griddata

from collections import OrderedDict
import os
from django.conf import settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def calculateThroughput(data):
    data["UserThR"].fillna(0, inplace=True)

    grouped = data.groupby("Time")["UserThR"]
    throughputDict = dict()
    throughputDict["Time"] = list()
    throughputDict["throughput"] = list()
    for time, throughput in grouped:
        pd.to_numeric(throughput, errors='coerce')
        throughput.replace("NaN", 0, inplace=True)
        # np.nansum(throughput)
        throughputDict["Time"].append(time)
        tempThroughput = np.nansum(throughput)
        throughputDict["throughput"].append(tempThroughput)

    nonZeroThroughputDict = 0
    i = 0
    for t in throughputDict["throughput"]:
        if t != 0:
            break
        else:
            i += 1

    nonZeroThroughputDict = {"Time": throughputDict["Time"][i:], "throughput": throughputDict["throughput"][i:]}


    return nonZeroThroughputDict


def displayDominateMap():
    # fig = Figure()
    # ax = fig.add_subplot(111)
    # canvas = FigureCanvas(fig)


    data = collection_read_mongo(collection="dominationmap")

    # fig = Figure()
    # canvas = FigureCanvas(fig)
    # matplotlib.rc('figure', figsize=(16, 12))

    X = np.array(data.iloc[:, 0])
    Y = np.array(data.iloc[:, 1])
    Z = np.array(data.iloc[:, 3])

    xi = np.linspace(X.min(), X.max(), 1000)
    yi = np.linspace(Y.min(), Y.max(), 1000)
    zi = griddata((X, Y), Z, (xi[None, :], yi[:, None]), method='cubic')

    zmin = -8
    zmax = 20
    zi[(zi < zmin) | (zi > zmax)] = None

    plt.contourf(xi, yi, zi, 15, cmap=plt.cm.rainbow, vmax=zmax, vmin=zmin)
    # storePath = settings.STATIC_URL + "fiveG/img/"
    # try:
    #     os.remove(storePath + "dominationMap.png")
    # except OSError:
    #     pass
    # plt.savefig(storePath + 'dominationMap.png')
    plt.savefig('dominationMap.png')


    # plt.save()
    # newDF = pd.DataFrame({"X": data.iloc[:, 0], "Y": data.iloc[:, 1], "Z": data.iloc[:, 3]})
    # data_pivoted = newDF.pivot("X", "Y", "Z")
    # ax = sns.heatmap(data_pivoted, vmin=-7, vmax=20, cmap=matplotlib.pyplot.cm.rainbow)
    # savefig("dominationmap.png")
    # # ax.add_image(sns.heatmap(newDF, vmin=-7, vmax=20, cmap=matplotlib.pyplot.cm.rainbow))
    #
    # # responsePNG = django.http.HttpResponse(content_type="image/png")
    # # canvas.print_png(responsePNG)
    return len(data.index)

#time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
def detectUnnormalCell():
    cellData = OrderedDict()
    cellData["CellID"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    cellData["Severity"] = ["Normal","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Minor","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Minor","Normal"]
    cellData["Created"] = ['2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51','2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51','2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51']
    cellData["Problem Class"] =["Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Temporary Low Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Temporary Low Traffic","Normal Traffic"]
    cellData["Service Class"] =["eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN"]

    return cellData










