'''
this file deals with data analysis
'''
import pandas as pd
import numpy as np


def calculateThroughput(data):
    data2 = data.fillna(0)
    grouped = data2.groupby("Time")["UserThR"]
    throughputDict = dict()
    throughputDict["Time"] = list()
    throughputDict["throughput"] = list()
    for time, throughput in grouped:
        # np.nansum(throughput)
        throughputDict["Time"].append(time)
        tempThroughput = np.nansum(throughput)
        throughputDict["throughput"].append(tempThroughput)

    return throughputDict


