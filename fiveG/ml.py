'''
this file deals with data analysis
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .models import collection_read_mongo, insert_document
from scipy.interpolate import griddata
from collections import OrderedDict
import os
from django.conf import settings
from sklearn import manifold

prev_thr = 0.0
last_time = 200
prev_time = 200
previous_thr = 0.0

def initialize_ml():
    prev_thr = 0.0
    last_time = 0.2


##############################################################
#   PREPROCESS DATA FOR GRAPHS TODO: MOVE ANOTHER FILE
##############################################################

def calculate_total_throughput_II(list_thr):
    """ UNDER CONSTRUCTION"""
    global prev_thr
    global last_time
    global prev_time

    list_thrs = []
    curr_time = int(list_thr[0]["Time"] * 100)
    curr_thr = 0.0

    count = 0
    for i in range(0, len(list_thr)):

        if prev_time == int(list_thr[i]["Time"] * 1000):
            curr_thr += list_thr[i]["Throughput"]
            count += 1
        else:
            prev_time = int(list_thr[i]["Time"] * 1000)
            thr = (curr_thr - prev_thr) / (1000000 * 0.2)
            list_thrs.append([list_thr[i]["Time"] - 0.2, thr])  # expecting timestep to be 200 ms
            prev_thr = curr_thr
            curr_thr = 0
            count = 0
        if i == (len(list_thr) - 1):    # TODO: Clean code
            prev_time = int(list_thr[i]["Time"] * 1000)
            thr = (curr_thr - prev_thr) / (1000000 * 0.2)
            list_thrs.append([list_thr[i]["Time"] - 0.2, thr])  # expecting timestep to be 200 ms
            prev_thr = curr_thr
            curr_thr = 0
            count = 0
    return list_thrs


def calculate_total_throughput(data_frame):
    """Calculates networks total throughput at each timestamp and puts it in dictionary"""
    global previous_thr
    # Initialize dictionary
    throughput_dict = dict()
    throughput_dict["time"] = list()
    throughput_dict["throughput"] = list()

    # Check if dataframe is empty
    if data_frame.empty:
        return throughput_dict

    # Set NaN values to zero (pandas)
    data_frame["Throughput"].fillna(0, inplace=True)
    # Group data (pandas)
    grouped = data_frame.groupby("Time")["Throughput"]

    previous_thr = 0.0
    previous_time = 0.0
    for time, throughput in grouped:
        pd.to_numeric(throughput, errors='coerce')
        throughput_dict["time"].append(time)
        current = np.nansum(throughput)
        elapsed_time = time - previous_time
        # divided by time and converted to -> megabit/s:
        throughput_dict["throughput"].append((current - previous_thr) / (1000000 * elapsed_time))
        previous_thr = current
        previous_time = time
    return throughput_dict


def get_rsrp_per_cell_from_collection_II(list_rsrp, dict_rsrp):
    """Calculates rsrp for each cell at each timestamp and puts them into dictionary"""
    # TODO: CURRENTLY EXPECTING FIRST USER ID TO 1
    # Calculate RSRP for each cell
    time_stamp = -1
    for i in list_rsrp:
        if time_stamp != i["Time"]:
            time_stamp = i["Time"]
            dict_rsrp["Time"].append(time_stamp)
        user_id = i["UserID"]  # Based on user id  we know
        key = "RSRP" + str(i["CellID"])
        if key not in dict_rsrp:
            dict_rsrp[key] = list()
        # Calculate average if timestamp is same
        if user_id > 1:
            dict_rsrp[key][-1] = (dict_rsrp[key][-1] + i["RSRP"]) / 2
        else:
            dict_rsrp[key].append(i["RSRP"])


def get_rsrp_per_cell_from_collection(list_rsrp):
    """Calculates rsrp for each cell at each timestamp and puts them into dictionary"""
    # TODO: CURRENTLY EXPECTING FIRST USER ID TO 1
    # Calculate RSRP for each cell
    dict_rsrp = dict()
    dict_rsrp["Time"] = list()  # WILL WE DO THIS IF LIST IS EMPTY??
    time_stamp = -1
    for i in list_rsrp:
        if time_stamp != i["Time"]:
            time_stamp = i["Time"]
            dict_rsrp["Time"].append(time_stamp)
        user_id = i["UserID"]  # Based on user id  we know
        key = "RSRP" + str(i["CellID"])
        if key not in dict_rsrp:
            dict_rsrp[key] = list()
        # Calculate average if timestamp is same
        if user_id > 1:
            dict_rsrp[key][-1] = (dict_rsrp[key][-1] + i["RSRP"]) / 2
        else:
            dict_rsrp[key].append(i["RSRP"])
    return dict_rsrp


##############################################################
#   END: PREPROCESS DATA FOR GRAPHS TODO: MOVE ANOTHER FILE
##############################################################


##############################################################
#   OUTPUT TO CSV TODO: MOVE ANOTHER FILE
##############################################################


def preprocessed_data_to_csv_file(path):
    """ Save preprocessed 8 dimensional data to CSV file and labels to another"""
    file = open(path + "simulation_data.csv", 'a')
    file_labels = open(path + "simulation_data_labels.csv", 'a')
    file.write("Time,UserID,LocationX,LocationY,RSRP1,RSRQ1,RSRP2,RSRQ2,RSRP3,RSRQ3,RSRP4,RSRQ4\n")
    file_labels.write("Label\n")
    file.close()
    file_labels.close()

    data = collection_read_mongo(collection="main_kpis_log_labels")
    processed = preprocess_data_8_dim(data)
    write_data_frame_to_csv_file(data_frame=processed, path=path)


# Move another location, function temporary located here
def write_data_frame_to_csv_file(data_frame, path):
    """ Writes dataframe to CSV file"""
    file = open(path + "simulation_data.csv", 'a')
    file_labels = open(path + "simulation_data_labels.csv", 'a')
    columns = list(data_frame)

    for i in range(0, len(data_frame["Time"])):
        comma = ""
        for col in columns:
            if col != "LABEL":
                file.write(comma + str(data_frame[col][i]))
                comma = ","
        file_labels.write(str(data_frame["LABEL"][i]) + "\n")
        file.write("\n")
    file.close()
    file_labels.close()


##############################################################
#   MACHINE LEARNING
##############################################################


def preprocess_data_8_dim(data):
    """ Preprocess data to data frame, columns:
        - Time UserID LABEL LocationX LocationY RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4"""
    id_list = list()
    pd.DataFrame(columns=["Time", "UserID", "LABEL", "LocationX", "LocationY"])
    signal_list = list()

    for identity, group in data.groupby(["Time", "UserID"]):
        # Pick the top 4 highest RSRP values and then its corresponding RSRQ values in that row
        top_4_row = group.sort_values(by=["RSRP"], ascending=False)[:4]
        try:
            signal_list.append([top_4_row.iloc[0]["RSRP"], top_4_row.iloc[0]["RSRQ"], top_4_row.iloc[1]["RSRP"],
                                top_4_row.iloc[1]["RSRQ"], top_4_row.iloc[2]["RSRP"], top_4_row.iloc[2]["RSRQ"],
                                top_4_row.iloc[3]["RSRP"], top_4_row.iloc[3]["RSRQ"]])
            id_list.append((round(identity[0], 1), identity[1], group["LABEL"].iloc[0], group["LocationX"].iloc[0], group["LocationY"].iloc[0]))
        except:
            pass # not good practice
    signal_df = pd.DataFrame(signal_list,
                            columns=["RSRP_1", "RSRQ_1", "RSRP_2", "RSRQ_2", "RSRP_3", "RSRQ_3", "RSRP_4", "RSRQ_4"])
    id_df = pd.DataFrame(id_list, columns=["Time", "UserID", "LABEL", "LocationX", "LocationY"])
    reference_df = id_df.merge(signal_df, left_index=True, right_index=True)
    return reference_df

def mds(data):
    '''
    preprocess data to make 8 dims and then apply mds(multidimensional scaling) to 3 dims vector, then make the reference database
    :param data:
    :return:
    '''
    # for each user A, we pick the top 4 highest RSRP, RSRQ value at a time point t.
    identiferList = list()
    pd.DataFrame(columns=["Time", "UserID", "LABEL", "LocationX", "LocationY"])
    # pd.DataFrame(columns=["Time", "UserID"])
    signalList = list()

    for ident, group in data.groupby(["Time", "UserID"]):
        #     iterate the group object, and pick the top 4 highest rsrp value and then its corresponsing rsrq value in that row
        #     print(type(group))
        top4Row = group.sort_values(by=["RSRP"], ascending=False)[:4]
        #     print(top4Row)
        try:
            signalRow = [top4Row.iloc[0]["RSRP"], top4Row.iloc[0]["RSRQ"], top4Row.iloc[1]["RSRP"],
                         top4Row.iloc[1]["RSRQ"], top4Row.iloc[2]["RSRP"], top4Row.iloc[2]["RSRQ"],
                         top4Row.iloc[3]["RSRP"], top4Row.iloc[3]["RSRQ"]]
            signalList.append(signalRow)
            ident = (round(ident[0], 1), ident[1], group["LABEL"].iloc[0], group["LocationX"].iloc[0],
                     group["LocationY"].iloc[0])
            #  ident = (round(ident[0], 1), ident[1])
            identiferList.append(ident)
        except:
            pass
    signalDF = pd.DataFrame(signalList,
                            columns=["RSRP_1", "RSRQ_1", "RSRP_2", "RSRQ_2", "RSRP_3", "RSRQ_3", "RSRP_4", "RSRQ_4"])
    identiferDF = pd.DataFrame(identiferList, columns=["Time", "UserID", "LABEL", "LocationX", "LocationY"])
    # identiferDF = pd.DataFrame(identiferList, columns=["Time", "UserID"])
    referenceDF = identiferDF.merge(signalDF, left_index=True, right_index=True)
    # TEMPORARY COMMENTED
    mds = manifold.MDS(3, max_iter=200, n_init=1)
    signalDF = signalDF.dropna(axis=0, how="any")
    threeDimSig = mds.fit_transform(signalDF)
    threeDimSigDF = pd.DataFrame(threeDimSig)

    # create a new Dataframe with merging two exist Dataframe, and length of these two dataframe is same
    referenceDF = identiferDF.merge(threeDimSigDF, left_index=True, right_index=True)


    return referenceDF


##############################################################
#   END: MACHINE LEARNING
##############################################################


##############################################################
#   NOT USED FUNCTIONS AND VARIABLES
##############################################################


# NOT USED ANYMORE???? - TUUKKA 9.3
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


# NOT USED ANYMORE???? - TUUKKA 9.3
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


# NOT USED ANYMORE - TUUKKA 9.3
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


##############################################################
#   END: NOT USED FUNCTIONS AND VARIABLES
##############################################################
