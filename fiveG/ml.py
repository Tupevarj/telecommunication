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

    return throughputDict


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
    return 0

def detectUnnormalCell():
    cellData = {"CellID": [10,1,2,5,3,1,18,3,4,30,8,4,14,27,5,7,11,6,19,22],
                "userID": [ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17,18, 19, 20],
                "signal": ['normal', 'normal', 'normal', 'weak', 'normal', 'normal', 'weak','normal', 'normal', 'weak', 'normal', 'normal', 'normal', 'normal','weak', 'weak', 'normal', 'normal', 'normal', 'normal']
                }



    return cellData










