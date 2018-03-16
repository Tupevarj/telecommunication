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
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
import math
import sys

prev_thr = 0.0
last_time = 200
prev_time = 200
previous_thr = 0.0

def initialize_ml():
    global prev_thr
    global last_time
    global prev_time
    prev_thr = 0.0
    last_time = 200
    prev_time = 200


##############################################################
#   PREPROCESS DATA FOR GRAPHS TODO: MOVE ANOTHER FILE
##############################################################

def calculate_total_throughput_III(data_frame):
    """ Calculated tota throughput at each timestamp, and stores values
        into list (Maybe faster than method II?)"""
    global prev_thr
    global last_time
    global prev_time

    list_thrs = []
    curr_thr = 0.0

    i = 0
    for time, thr in data_frame.groupby(["Time", "Throughput"]):

        if prev_time == int(time * 1000):
            curr_thr += thr
        else:
            if not i == 0:
                total_thr = (curr_thr - prev_thr) / (1000000 * 0.2)
                list_thrs.append([prev_time / 1000.0, total_thr])  # expecting timestep to be 200 ms
                prev_thr = curr_thr
                curr_thr = 0
            prev_time = int(time * 1000)
        if i == (len(data_frame) - 1):  # TODO: Clean code
            prev_time = int(time * 1000)
            total_thr = (curr_thr - prev_thr) / (1000000 * 0.2)
            list_thrs.append([prev_time / 1000.0, total_thr])  # expecting timestep to be 200 ms
            prev_thr = curr_thr
            curr_thr = 0
        i += 1
    return list_thrs



def calculate_total_throughput_II(list_thr):
    """ Calculated tota throughput at each timestamp, and stores values
        into list """
    global prev_thr
    global last_time
    global prev_time

    list_thrs = []
    curr_thr = 0.0

    for i in range(0, len(list_thr)):

        if prev_time == int(list_thr[i]["Time"] * 1000):
            curr_thr += list_thr[i]["Throughput"]
        else:
            if not i == 0:
                thr = (curr_thr - prev_thr) / (1000000 * 0.2)
                list_thrs.append([prev_time/1000.0, thr])  # expecting timestep to be 200 ms
                prev_thr = curr_thr
                curr_thr = 0
            prev_time = int(list_thr[i]["Time"] * 1000)
        if i == (len(list_thr) - 1):    # TODO: Clean code
            prev_time = int(list_thr[i]["Time"] * 1000)
            thr = (curr_thr - prev_thr) / (1000000 * 0.2)
            list_thrs.append([prev_time/1000.0, thr])  # expecting timestep to be 200 ms
            prev_thr = curr_thr
            curr_thr = 0
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

simpleRegressor = LinearRegression()
dtRegressor = DecisionTreeRegressor(random_state=0)
rfRegressor = RandomForestRegressor(n_estimators=10, random_state=0)
svrRegressor = SVR(kernel='rbf')
linRegressor = LinearRegression()


def preprocess_training_set_locations(array_x, array_y, data_frame):
    # Converting RSRP and RSRQ values into floats
    i_max = len(data_frame)
    for i in range(0, i_max):
        dataset_row = data_frame.iloc[i][['Time', 'UserID', 'RSRP_1', 'RSRQ_1', 'RSRP_2', 'RSRQ_2', 'RSRP_3', 'RSRQ_3', 'RSRP_4', 'RSRQ_4']]

        if not np.isnan(dataset_row['RSRQ_1']):
            array_x.append([dataset_row['Time'], dataset_row['UserID'], dataset_row['RSRP_1'], dataset_row['RSRQ_1'], dataset_row['RSRP_2'], dataset_row['RSRQ_2'], dataset_row['RSRP_3'], dataset_row['RSRQ_3'], dataset_row['RSRP_4'], dataset_row['RSRQ_4']])
            array_y.append(bool(data_frame.iloc[i]["LABEL"]))
        #
        # # print(dataset.iloc[i])
        # for j in range(0, 10):
        #     value = float(dataset_row[j])
        #     if not np.isnan(value):
        #         row.append(float(dataset_row[j]))
        #     else:
        #         skip = True
        # if not skip:


def preprocess_training_set(array_x, array_y, data_frame):
    """ Preprocess data-frame for training phase"""
    i_max = len(data_frame)
    for i in range(0, i_max):
        row = []
        skip = False
        dataset_row = data_frame.iloc[i]
        for j in range(5, 12):
            value = float(dataset_row[j])
            if not np.isnan(value):
                row.append(float(dataset_row[j]))
            else:
                skip = True
                break
        if not skip:
            array_x.append(row)
            array_y.append(bool(data_frame['LABEL'][i]))


def train_and_test_simple_regression(array_x, array_y, roc_auc):
    """ Training for simple regression"""
    global simpleRegressor

    x_train, x_test, y_train, y_test = train_test_split(array_x, array_y, test_size=0.2, random_state=0)

    simpleRegressor.fit(np.asarray(array_x), np.asarray(array_y))
    y_pred = simpleRegressor.predict(np.asarray(x_test))

    actual = y_test
    predictions = y_pred

    false_positive_rate, true_positive_rate, thresholds = roc_curve(actual, predictions)

    roc_auc[0] = auc(false_positive_rate, true_positive_rate)

    list_points = list()
    for i in range(0, len(false_positive_rate)):
        list_points.append([false_positive_rate[i], true_positive_rate[i]])

    return list_points


def train_and_test_random_forest_regression(array_x, array_y, roc_auc):
    """ Training for random forest regression"""
    global rfRegressor

    X_train, X_test, y_train, y_test = train_test_split(array_x, array_y, test_size=0.2, random_state=0)

    rfRegressor.fit(X_train, y_train)
    y_pred = rfRegressor.predict(np.asarray(X_test))

    actual = y_test
    predictions = y_pred

    false_positive_rate, true_positive_rate, thresholds = roc_curve(actual, predictions)

    roc_auc[0] = auc(false_positive_rate, true_positive_rate)

    list_points = list()
    for i in range(0, len(false_positive_rate)):
        list_points.append([false_positive_rate[i], true_positive_rate[i]])

    return list_points


def train_and_test_decision_tree(array_x, array_y, roc_auc):
    """ Training for random decision tree regression"""
    global dtRegressor

    # splitting of data
    X_train, X_test, y_train, y_test = train_test_split(array_x, array_y, test_size=0.2, random_state=0)

    dtRegressor.fit(X_train, y_train)

    # pridicting a new result
    y_pred = dtRegressor.predict(np.asarray(X_test))

    actual = y_test
    predictions = y_pred

    false_positive_rate, true_positive_rate, thresholds = roc_curve(actual, predictions)

    roc_auc[0] = auc(false_positive_rate, true_positive_rate)

    list_points = list()
    for i in range(0, len(false_positive_rate)):
        list_points.append([false_positive_rate[i], true_positive_rate[i]])

    return list_points


def train_and_test_svr(array_x, array_y, roc_auc):
    """ Training for SVR (regression?)"""
    global svrRegressor
    # splitting of data
    # X_train, X_test, y_train, y_test= train_test_split(array_x,array_y,test_size = 0.2, random_state=0)

    # Fitting SVR to the dataset
    svrRegressor.fit(array_x, array_y)

    y_pred = svrRegressor.predict(np.asarray(array_x))

    # print (len(y_test))
    actual = array_y
    predictions = y_pred

    false_positive_rate, true_positive_rate, thresholds = roc_curve(actual, predictions)

    roc_auc[0] = auc(false_positive_rate, true_positive_rate)

    list_points = list()
    for i in range(0, len(false_positive_rate)):
        list_points.append([false_positive_rate[i], true_positive_rate[i]])

    return list_points


def train_and_test_distance(array_x, array_y, dataset_stimulation):
    """ Training for distance???"""
    global linRegressor
    # splitting of data
    X_train, X_test, y_train, y_test = train_test_split(array_x, array_y, test_size=0.2, random_state=7)

    # Regression Classification
    linRegressor.fit(np.asarray(X_train), np.asarray(y_train))

    y_pred = linRegressor.predict(np.asarray(X_test))

    store_pred = []
    actual = y_test
    predictions = y_pred
    y_pred_lenght = len(y_pred)
    for i in range(0, y_pred_lenght):
        store_pred.append(y_pred[i])

    index_values = []
    for i in range(0, len(store_pred)):
        if store_pred[i] >= 0.1:
            # print ( store_pred[i])
            index_values.append([X_test[i][0], X_test[i][1], store_pred[i]])

    # print (index_values)   # user loc + user id + predicted value    abnormal users

    dataset_basestations = pd.read_csv("/home/tupevarj/Desktop/basestations.csv")  # TODO: read data from csv file

    bsatations = []

    for i in range(0, 7):
        dict_base_station = dict()
        dict_base_station['base_station_id'] = dataset_basestations['Basestation'][i]
        dict_base_station['LocationX'] = dataset_basestations['LocationX'][i]
        dict_base_station['LocationY'] = dataset_basestations['LocationY'][i]
        string_cell_ids = dataset_basestations['CellIDs'][i].split(',')
        ids_int = list()
        for id in range(0, 3):
            ids_int.append(int(string_cell_ids[id]))
        dict_base_station['Cellids'] = ids_int
        bsatations.append(dict_base_station)


    # TODO: CHANGE HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # dataset_stimulation = pd.read_csv("/home/buzafar/Documents/simulation_data.csv")
    array_user = []

    for i in range(0, len(index_values)):
        id_user = int(index_values[i][1]) - 1
        time_stamp = index_values[i][0]  # 200 milliseconds

        adfs = time_stamp / 0.2
        int_adfs = int(adfs)
        modulo = adfs % int_adfs
        if modulo > 0.5:
            adfs = math.ceil(adfs)
        else:
            adfs = int_adfs
        actual_index = int(105 * (adfs - 1) + id_user)
        array_user.append([dataset_stimulation.iloc[actual_index][0], dataset_stimulation.iloc[actual_index][1],
                           dataset_stimulation.iloc[actual_index][2], dataset_stimulation.iloc[actual_index][3]])

    l = []  # list to store user_id,basestation_id,computed distance, time of user
    Matrix = []

    for i in range(0, len(array_user)):  # rows
        pb = array_user[i][2], array_user[i][3]
        # row = []
        min_distance = sys.float_info.max
        base_station_id = -1
        all_distances = []
        for station in range(0, 7):  # base stations columns
            pa = bsatations[station]["LocationX"], bsatations[station]["LocationY"]
            distance = math.sqrt(((pa[0] - pb[0]) ** 2) + ((pa[1] - pb[1]) ** 2))
            all_distances.append(distance)
            if distance < min_distance:
                min_distance = distance
                base_station_id = station + 1

        Matrix.append(all_distances)

        l.append([array_user[i][0], array_user[i][1], base_station_id, min_distance])

    dict_users_per_bs = dict()
    for i in range(0, 7):
        dict_users_per_bs["BS" + str(i + 1)] = 0

    for i in range(0, len(l)):
        key = "BS" + str(l[i][2])
        dict_users_per_bs[key] += 1

    # calculate z-score

    z1score = list()
    for i in range(0, 7):
        total_score = dict_users_per_bs['BS' + str(i + 1)]
        bs_sum = 0
        array_store = list()
        for j in range(0, 7):
            if not j == i:
                array_store.append(dict_users_per_bs["BS" + str(j + 1)])
                bs_sum += dict_users_per_bs["BS" + str(j + 1)]
        bs1_mean = bs_sum / 6.0
        differences = ([x - bs1_mean for x in array_store])
        sq_differences = [d ** 2 for d in differences]
        ssd = sum(sq_differences)
        variance = float(ssd / 6.0)  # six basestations
        z1score.append(abs(total_score - bs1_mean) / math.sqrt(variance))

    return z1score


def do_z_score_regression(data_frame, data_unprocessed):
    array_x = []
    array_y = []
    preprocess_training_set_locations(array_x, array_y, data_frame)
    data = data_frame[['Time', 'UserID', 'LocationX', 'LocationY', 'RSRP_1', 'RSRQ_1', 'RSRP_2', 'RSRQ_2', 'RSRP_3', 'RSRQ_3', 'RSRP_4', 'RSRQ_4']]
    return train_and_test_distance(array_x=array_x, array_y=array_y,dataset_stimulation=data)


def do_svr_regression(data_frame, roc_auc):
    array_x = []
    array_y = []
    preprocess_training_set(array_x, array_y, data_frame)
    return train_and_test_svr(array_x, array_y, roc_auc)


def do_decision_tree_regression(data_frame, roc_auc):
    array_x = []
    array_y = []
    preprocess_training_set(array_x, array_y, data_frame)
    return train_and_test_decision_tree(array_x, array_y, roc_auc)


def do_random_forest_regression(data_frame, roc_auc):
    array_x = []
    array_y = []
    preprocess_training_set(array_x, array_y, data_frame)
    return train_and_test_random_forest_regression(array_x, array_y, roc_auc)


def do_simple_regression(data_frame, roc_auc):
    array_x = []
    array_y = []
    preprocess_training_set(array_x, array_y, data_frame)
    return train_and_test_simple_regression(array_x, array_y, roc_auc)


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
