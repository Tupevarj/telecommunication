'''
this file deals with data analysis
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .models import normalCol_read_mongo, collection_read_mongo, insert_document
from scipy.interpolate import griddata
from collections import OrderedDict
import os
from django.conf import settings


def calculateThroughput(data):
    data["UserThR"].fillna(0, inplace=True)

    grouped = data.groupby("Time")["UserThR"]
    throughputDict = dict()
    throughputDict["Time"] = list()
    throughputDict["throughput"] = list()
    for time, throughput in grouped:
        pd.to_numeric(throughput, errors='coerce')
        throughput.replace("NaN", 0, inplace=True)
        throughputDict["Time"].append(time)
        tempThroughput = np.nansum(throughput)
        throughputDict["throughput"].append(np.asscalar(tempThroughput))

    nonZeroThroughputDict = 0
    i = 0
    for t in throughputDict["throughput"]:
        if t != 0:
            break
        else:
            i += 1

    nonZeroThroughputDict = {"Time": throughputDict["Time"][i:], "throughput": throughputDict["throughput"][i:]}
    return nonZeroThroughputDict

def calculateRSRP(data):
    # replace nan value with 0 in RSRP column
    data["RSRP"].fillna(0, inplace=True)

    grouped = data.groupby(["Time", "CellID"])["RSRP"]

    RSRPDict = dict()
    RSRPDict["Time"] = list()
    RSRPDict[1] = list()
    RSRPDict[2] = list()
    RSRPDict[3] = list()

    for k, rsrp in grouped:
        if k[1] in (1,2,3):
            RSRPDict["Time"].append(k[0])
            RSRPDict[k[1]].append(sum(rsrp))
        else:#means not the specific cells
            pass

    return {"Time": RSRPDict["Time"], "RSRP_1": RSRPDict[1], "RSRP_2": RSRPDict[2], "RSRP_3": RSRPDict[3]}







def displayDominateMap():

    data = collection_read_mongo(collection="dominationmap")

    X = np.array(data["x"])
    Y = np.array(data["y"])
    Z = np.array(data["sinr"])

    xi = np.linspace(float(X.min()), float(X.max()), 1000)
    yi = np.linspace(Y.min(), Y.max(), 1000)
    zi = griddata((X, Y), Z, (xi[None, :], yi[:, None]), method='cubic')

    zmin = -8
    zmax = 20
    zi[(zi < zmin) | (zi > zmax)] = None

    plt.contourf(xi, yi, zi, 15, cmap=plt.cm.rainbow, vmax=zmax, vmin=zmin)
    try:
        os.remove(settings.MEDIA_ROOT + "dominationMap.png")
    except OSError:
        pass
    plt.savefig("dominationMap.png")

    fig = plt.gcf()
    fig.set_size_inches(4.8, 3.6)
    fig.savefig(settings.MEDIA_ROOT+'dominationMap.png')

    return len(data.index)

def detectUnnormalCell():
    cellData = OrderedDict()
    cellData["CellID"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    cellData["Severity"] = ["Normal","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Minor","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Minor","Normal"]
    cellData["Created"] = ['2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51','2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51','2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51']
    cellData["Problem Class"] =["Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Temporary Low Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Temporary Low Traffic","Normal Traffic"]
    cellData["Service Class"] =["eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN"]

    return cellData










