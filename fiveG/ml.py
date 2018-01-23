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
    fig = plt.gcf()
    fig.set_size_inches(4.8, 3.6)
    fig.savefig(settings.MEDIA_ROOT+'dominationMap.png')

    return len(data.index)

def detectUnnormalCell():
    '''
    use RSRP variable to detect the whether the cell is normal or not
    :return:
    '''
    # cellData = OrderedDict()
    # cellData["CellID"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    # cellData["Severity"] = ["Normal","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Minor","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Normal","Minor","Normal"]
    # cellData["Created"] = ['2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51','2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51','2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51', '2017-12-04 12:34:51']
    # cellData["Problem Class"] =["Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Temporary Low Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Normal Traffic","Temporary Low Traffic","Normal Traffic"]
    # cellData["Service Class"] =["eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN","eUTRAN"]

    # return cellData

    # data = collection_read_mongo(collection="main_file_with_UserTHR")
    # groupedData = data.groupby(["Time", "CellID"])["RSRP"].sum()
    #
    # rsrpUpper = getThreshold(groupedData, time_interval=30)["upper"]
    # rsrpLower = getThreshold(groupedData)["lower"]

    # this number should be decided by applying ML algorithm
    data = collection_read_mongo(collection="TUUKKA_throughputs")
    groupedData = data.groupby(["Time", "CellID"])["Throughput"]

    trafficUPThreshold = 10000
    trafficDOWNThreshold = 1000
    records = list()
    throughputList = list()
    for k, throughput in groupedData:
        record = list()
        totalThroughput = sum(throughput)
        throughputList.append(totalThroughput)
        # k[1] means cell ID
        record.append(k[1])
        # k[0] is time variable
        record.append(k[0])
        record.append(totalThroughput)
        if totalThroughput < trafficDOWNThreshold:
            record.append("Minor")
            record.append("Temporary Low Traffic")
        elif totalThroughput > trafficUPThreshold:
            record.append("Over")
            record.append("Temporary high Traffic")
        else:
            record.append("Normal")
            record.append("Normal Traffic")
        record.append("eUTRAN")
        records.append(record)
    # create new dataframe which stores "Time", "CellID", "totalThroughputForThisCellAtThisTime"
    df = pd.DataFrame(records, columns=["CellID", "Time", "totalThroughput","Severity", "Problem Class", "Service Class"])

    return df


def getThreshold(data, time_interval=30):
    '''
    calculate the upper bound threshold and lower bound threshold
    data["time"] list of time series
    data["rsrp"] list of double
    time_interval default 30 seconds, with containing 5 whole periods
    :return dictionary

    '''

    upper = 0
    lower = 0
    avg = np.mean(data["rsrp"])
    std = np.std(data["rsrp"])
    k = 3
    upper = avg + k * std
    lower = avg + k * std

    return {"upper": upper, "lower": lower}


def getVectorRSRP(data):
    '''
    generate rsrp vector and its traffic label
    :return:
    '''

    # get all total rsrp for all cells for each user
    grouped = data.groupby(["Time", "UserID"])["RSRP"]
    time_interval = 5
    l = list()
    for k, rsrp in grouped:
        totalRSRP = np.sum(rsrp)
        l.append([k[0], k[1], totalRSRP])

    df = pd.DataFrame(l, columns=["Time", "Cell", "TotalRSRP"])


    # get specific section of dataframe between specific time slot

    latestTime = max(df["Time"])

    repeatTimes = int(latestTime / time_interval) + 1
    # for i in range(repeatTimes):
    #     if


def calculateAvgRSRPForCell(data):
    grouped = data.groupby("cell")["TotalRSRP"]


    rsrpCells = dict()
    rsrpCells[1] = 0
    rsrpCells[2] = 0
    return rsrpCells



def detectCellREAL():
#     preprocess data to get the specific dataframe
    data = collection_read_mongo(collection="main_file_with_UserTHR")
    preparedDF = preprocessDF(data)

# apply machine learning algorithm here




def preprocessDF(data):
    '''
    process the raw dataframe and then put the processed data into machine learning part
    :param rawData:
    :return: dataframe
    '''

    testData = data[:10000]

    wantedDF = pd.DataFrame(
        columns=["Time", "User", "LocationX", "LocationY", "RSRP_1st", "1stRSRP_Corresponding_RSRQ", "Serving_Cell",
                 "RSRP_2nd", "2ndRSRP_Corresponding_RSRQ", "RSRP_3rd", "3rdRSRP_Corresponding_RSRQ", "RSRP_4th",
                 "4thRSRP_Corresponding_RSRQ"])
    i = 0
    for stamp, group in testData.groupby(["Time", "UserID"]):
        #     rsrp_top3 = [0,0,0]
        #     rsrp_matched_record_index = [0, 0,0]
        rsrpIndexList = list()
        for i in range(group.shape[0]):
            rsrpIndexList.append((i, group["RSRP"][i]))
        rsrpIndexListSorted = sorted(rsrpIndexList, key=lambda x: x[1], reverse=True)
        row_rsrp1st = group.iloc[rsrpIndexListSorted[0][0]]
        a = row_rsrp1st["Time"]
        b = int(row_rsrp1st["UserID"])
        c = row_rsrp1st["LocationX"]
        d = row_rsrp1st["LocationY"]
        e = row_rsrp1st["RSRP"]
        f = row_rsrp1st["RSRQ"]
        g = int(row_rsrp1st["CellID"])
        h = group.iloc[rsrpIndexListSorted[1][0]]["RSRP"]
        p = group.iloc[rsrpIndexListSorted[1][0]]["RSRQ"]
        k = group.iloc[rsrpIndexListSorted[2][0]]["RSRP"]
        l = group.iloc[rsrpIndexListSorted[2][0]]["RSRQ"]
        m = group.iloc[rsrpIndexListSorted[3][0]]["RSRP"]
        n = group.iloc[rsrpIndexListSorted[3][0]]["RSRQ"]
        wantedDF.loc[i] = [a, b, c, d, e, f, g, h, p, k, l, m, n]
        i += 1


    return wantedDF


























