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


def calculate_total_throughput(data_frame):
    """Calculates networks total throughput at each timestamp and puts it in dictionary"""
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

def detectCellREAL():
#     preprocess data to get the specific dataframe
    data = collection_read_mongo(collection="main_file_with_UserTHR")
    preparedDF = preprocessDF(data)

# apply anormaly detection model machine learning algorithm here





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

def mds(data):
    '''
    :param data:
    :return:
    '''
    # for each user A, we pick the top 4 highest RSRP, RSRQ value at a time point t.
    identiferList = list()
    pd.DataFrame(columns=["Time", "UserID"])
    signalList = list()

    for ident, group in testData.groupby(["Time", "UserID"]):
        #     iterate the group object, and pick the top 4 highest rsrp value and then its corresponsing rsrq value in that row
        #     print(type(group))
        top4Row = group.sort_values(by=["RSRP"])[:4]
        #     print(top4Row)
        try:
            signalRow = [top4Row.iloc[0]["RSRP"], top4Row.iloc[0]["RSRQ"], top4Row.iloc[1]["RSRP"],
                         top4Row.iloc[1]["RSRQ"], top4Row.iloc[2]["RSRP"], top4Row.iloc[2]["RSRQ"],
                         top4Row.iloc[3]["RSRP"], top4Row.iloc[3]["RSRQ"]]
            signalList.append(signalRow)
            ident = (round(ident[0], 1), ident[1])
            identiferList.append(ident)
        except:
            pass




    return referenceDF
























from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
import math
import sys
from sklearn.model_selection import cross_val_score,cross_val_predict
from sklearn.externals import joblib
from enum import Enum
from .models import collection_update_with_set, read_mongo_guaranteed
import time


##############################################################
#   MACHINE LEARNING
##############################################################


class Regressor(Enum):
    SIMPLE_REG = 0
    DECISION_TREE_REG = 1
    RANDOM_FOREST_REG = 2
    SVR_REG = 3


sel_reg_enum = Regressor.SIMPLE_REG     # Currently selected regressor TODO: maybe store in another file
regressors_chart_data = [0, 0, 0, 0]    # Points for graph showing performance of regressors
regressors_table_data = [0, 0, 0, 0]    # AUC scores showing performance of regressors
z_scores_ref = [dict(), dict(), dict(), dict()]             # Reference Z-scores
regressors = [LinearRegression(),       # List of available regressors
              DecisionTreeRegressor(random_state=0),
              RandomForestRegressor(n_estimators=10, random_state=0),
              SVR(kernel='rbf')]


#######################################
#   GETTERS / SETTERS
#######################################


def set_regressor(reg_enum):
    """ Sets current regressor """
    global sel_reg_enum
    sel_reg_enum = Regressor(reg_enum)


def get_ref_z_scores(reg_enum):
    """ Return reference Z-scores based on enum value."""
    global z_scores_ref
    return z_scores_ref[reg_enum.value]


def get_reg_chart_data():
    """ Return regressors chart data """
    global regressors_chart_data
    return regressors_chart_data


def get_auc_scores():
    """ Return regressors AUC scores """
    global regressors_table_data
    return regressors_table_data


def get_reg_z_scores():
    """ Return regressors reference Z-scores """
    global z_scores_ref
    return z_scores_ref


def get_current_z_scores():
    """ Return current Z-scores """
    global sel_reg_enum
    return z_scores_ref[sel_reg_enum.value]


#######################################
#   END: GETTERS / SETTERS
#######################################


#######################################
#   SAVE AND LOAD REGRESSORS
#######################################


def write_xy_to_csv_file(list_xy, file_name):
    """ Writes list of tuples to CSV file """
    file = open(file_name, 'w')
    file.write("X,Y\n")
    for i in range(0, len(list_xy)):
        file.write(str(list_xy[i][0]) + "," + str(list_xy[i][1]) + "\n")
    file.close()


def save_all_regressors():
    """ Save all trained regressors and testing values to hard drive"""
    global regressors
    global regressors_chart_data
    global regressors_table_data

    # Save regressors
    joblib.dump(regressors[Regressor.SIMPLE_REG.value], 'simple_reg.pkl')
    joblib.dump(regressors[Regressor.DECISION_TREE_REG.value], 'dt_reg.pkl')
    joblib.dump(regressors[Regressor.RANDOM_FOREST_REG.value], 'rf_reg.pkl')
    joblib.dump(regressors[Regressor.SVR_REG.value], 'svr_reg.pkl')

    # Save testing values of regressors
    write_xy_to_csv_file(regressors_chart_data[Regressor.SIMPLE_REG.value], "data_simple_reg.csv")
    write_xy_to_csv_file(regressors_chart_data[Regressor.DECISION_TREE_REG.value], "data_dt_reg.csv")
    write_xy_to_csv_file(regressors_chart_data[Regressor.RANDOM_FOREST_REG.value], "data_rf_reg.csv")
    write_xy_to_csv_file(regressors_chart_data[Regressor.SVR_REG.value], "data_svr_reg.csv")
    file = open("regressors_aucs.csv", 'w')
    file.write(str(regressors_table_data[Regressor.SIMPLE_REG.value]) + "," + str(regressors_table_data[Regressor.DECISION_TREE_REG.value]) + "," +
               str(regressors_table_data[Regressor.RANDOM_FOREST_REG.value]) + "," + str(regressors_table_data[Regressor.SVR_REG.value]))
    file.close()
    file = open("z_scores.csv", 'w')
    for i in range(0, len(z_scores_ref)):
        comma = ""
        for j in range(0, len(z_scores_ref[i]["Ref. Z-scores"])):
            file.write(comma + str(z_scores_ref[i]["Ref. Z-scores"][j]))
            comma = ","
        file.write("\n")
    file.close()
    return 1


def load_all_regressors():
    """ Load all previously saved regressors from hard drive"""
    global training_done
    global regressors
    global regressors_chart_data
    global regressors_table_data
    global z_scores_ref
    try:
        regressors[Regressor.SIMPLE_REG.value] = joblib.load('simple_reg.pkl')
        regressors[Regressor.DECISION_TREE_REG.value] = joblib.load('dt_reg.pkl')
        regressors[Regressor.RANDOM_FOREST_REG.value] = joblib.load('rf_reg.pkl')
        regressors[Regressor.SVR_REG.value] = joblib.load('svr_reg.pkl')

        simple_data = pd.read_csv("data_simple_reg.csv")
        regressors_chart_data[Regressor.SIMPLE_REG.value] = (np.array(simple_data)).tolist()
        dt_data = pd.read_csv("data_dt_reg.csv")
        regressors_chart_data[Regressor.DECISION_TREE_REG.value] = (np.array(dt_data)).tolist()
        rf_data = pd.read_csv("data_rf_reg.csv")
        regressors_chart_data[Regressor.RANDOM_FOREST_REG.value] = (np.array(rf_data)).tolist()
        svr_data = pd.read_csv("data_svr_reg.csv")
        regressors_chart_data[Regressor.SVR_REG.value] = (np.array(svr_data)).tolist()

        auc_data = pd.read_csv("regressors_aucs.csv", header=None)
        z_scores = pd.read_csv("z_scores.csv", header=None)

        z_scores_list = (np.array(z_scores)).tolist()
        for i in range(0, len(z_scores_list)):
            z_scores_ref[i]["BS"] = get_cell_ids()
            z_scores_ref[i]["Ref. Z-scores"] = z_scores_list[i]

        regressors_table_data[Regressor.SIMPLE_REG.value] = auc_data.iloc[0][0]
        regressors_table_data[Regressor.DECISION_TREE_REG.value] = auc_data.iloc[0][1]
        regressors_table_data[Regressor.RANDOM_FOREST_REG.value] = auc_data.iloc[0][2]
        regressors_table_data[Regressor.SVR_REG.value] = auc_data.iloc[0][3]

        training_done = True

        return 1
    except:     # Files not found..
        return 0


#######################################
#   END: SAVE AND LOAD REGRESSORS
#######################################


#######################################
#   TRAIN AND TEST OF REGRESSORS
#######################################

def train_all_regressors(x_train, y_train):
    global regressors
    for reg in regressors:
        reg.fit(x_train, y_train)


def test_regressor(reg_enum, test_data, correct_answers):
    """ Test regressor with test set and correct answers
        Updates regression chart_data and regression table_data accordingly """
    global regressors_chart_data
    global regressors_table_data
    global regressors
    predictions = cross_val_predict(regressors[reg_enum.value], test_data, correct_answers, cv=6)
    false_positive_rate, true_positive_rate, thresholds = roc_curve(correct_answers, predictions)

    regressors_chart_data[reg_enum.value] = list(zip(false_positive_rate, true_positive_rate))
    regressors_table_data[reg_enum.value] = auc(false_positive_rate, true_positive_rate)


def train_and_test_all_regressions(array_x, array_y):
    """ Train and test each regressor. Get points and auc values for each classifier """
    global training_done
    x_train, x_test, y_train, y_test = train_test_split(array_x, array_y, test_size=0.2, random_state=7)

    # Train all regressors
    train_all_regressors(x_train=x_train, y_train=y_train)

    # Test all regressors
    test_regressor(Regressor.SIMPLE_REG, x_test, y_test)
    test_regressor(Regressor.DECISION_TREE_REG, x_test, y_test)
    test_regressor(Regressor.RANDOM_FOREST_REG, x_test, y_test)
    test_regressor(Regressor.SVR_REG, x_test, y_test)

    training_done = True


#######################################
#   END: TRAIN AND TEST OF REGRESSORS
#######################################

#######################################
#   RUN ML ALGORITHMS
#######################################

def calculate_z_scores(predictions, x_test):
    """ Calculates z-scores based on predictions from regressor,
        also needs to have data containing user locations"""
    dataset_basestations = pd.read_csv("basestations.csv")  # TODO: make it read from DB

    # Calculate number users that are closest to cell:
    list_ues_per_bs = [0] * 7
    for i in range(0, len(predictions)):
        if predictions[i] >= 0.1:
            min_distance = sys.float_info.max
            base_station_id = -1
            for j, bs in dataset_basestations.iterrows():
                distance = math.sqrt(((bs["LocationX"] - x_test[i][2]) ** 2) + ((bs["LocationY"] - x_test[i][3]) ** 2))
                if distance < min_distance:
                    min_distance = distance
                    base_station_id = j
            list_ues_per_bs[base_station_id] += 1

    # Define Z-scores
    z1score = list()
    for i in range(0, 7):
        mean = (sum(list_ues_per_bs) - list_ues_per_bs[i]) / 6.0
        variance = 0.0
        for j in range(0, 7):
            if not j == i:
                variance += ((list_ues_per_bs[j] - mean) ** 2) / 6.0
        variance = 1.0 if variance == 0.0 else variance     # Change variance to 1.0 if 0.0
        z1score.append(abs(list_ues_per_bs[i] - mean) / math.sqrt(variance))

    return z1score


def get_cell_ids():
    cell_ids = list()
    for i in range(0, 7):
        cell_ids.append("Cell " + str(i+1))        #FIXME !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    return cell_ids


def calculate_reference_z_scores(array_x, array_y):
    """ Calculates reference z-score for each regressor """
    global regressors
    global z_scores_ref
    x_train, x_test, y_train, y_test = train_test_split(array_x, array_y, test_size=0.2, random_state=7)
    predictions = regressors[Regressor.SIMPLE_REG.value].predict(np.asarray(x_test)[:, 4:])
    z_scores_ref[Regressor.SIMPLE_REG.value]["Ref. Z-scores"] = calculate_z_scores(predictions, x_test)
    z_scores_ref[Regressor.SIMPLE_REG.value]["BS"] = get_cell_ids()
    predictions = regressors[Regressor.DECISION_TREE_REG.value].predict(np.asarray(x_test)[:, 4:])
    z_scores_ref[Regressor.DECISION_TREE_REG.value]["Ref. Z-scores"] = calculate_z_scores(predictions, x_test)
    z_scores_ref[Regressor.DECISION_TREE_REG.value]["BS"] = get_cell_ids()
    predictions = regressors[Regressor.RANDOM_FOREST_REG.value].predict(np.asarray(x_test)[:, 4:])
    z_scores_ref[Regressor.RANDOM_FOREST_REG.value]["Ref. Z-scores"] = calculate_z_scores(predictions, x_test)
    z_scores_ref[Regressor.RANDOM_FOREST_REG.value]["BS"] = get_cell_ids()
    predictions = regressors[Regressor.SVR_REG.value].predict(np.asarray(x_test)[:, 4:])
    z_scores_ref[Regressor.SVR_REG.value]["Ref. Z-scores"] = calculate_z_scores(predictions, x_test)
    z_scores_ref[Regressor.SVR_REG.value]["BS"] = get_cell_ids()
    return z_scores_ref


def run_ml(array_x):
    """ Run machine learning once. Returns ID of broken cell.
        Based on comparing reference and new z-scores """
    global sel_reg_enum
    predictions = regressors[sel_reg_enum.value].predict(np.asarray(array_x)[:, 4:])
    z_score_ref = get_ref_z_scores(sel_reg_enum)
    z_scores_new = dict()
    z_scores_new['BS'] = get_cell_ids()
    z_scores_new['Ref. Z-scores'] = get_ref_z_scores(sel_reg_enum)['Ref. Z-scores']
    z_scores_new['Z Score'] = calculate_z_scores(predictions, array_x)

    high4 = [0, -1]
    for i in range(0, 7):
        if high4[1] < z_scores_new["Z Score"][i]:
            high4[1] = z_scores_new["Z Score"][i]
            high4[0] = i + 1
            #high4[2] = z_scores_new[i]
            score_outage = []
    for i in range(0, 7):
       # if i == 3 and z_scores_new[i] == high4[1]:
       #     score_outage.append(i)
        if z_scores_new["Z Score"][i] >= z_score_ref['Ref. Z-scores'][i]:
            score_outage.append(i)
            maxval = [0, -1]

    for i in range(0, len(score_outage)):
        if maxval[1] < z_scores_new["Z Score"][score_outage[i]]:
            maxval[1] = z_scores_new["Z Score"][score_outage[i]]
            maxval[0] = score_outage[i] + 1
            #maxval[2] = z_scores_new[score_outage[i]]

    if maxval[1] >= 0.3:
        return [maxval[0], z_scores_new]
    else:
        return [0, z_scores_new]

    # OLD CODE
    # for i in range(0, 7):
    #     if z_scores_new[i] >= z_scores_ref[i] and z_scores_new[i] > highest_z_score:
    #         outage_id = i +1
    #         highest_z_score = z_scores_new[i]

#######################################
#   END: RUN ML ALGORITHMS
#######################################


def get_number_of_cells():
    """ Returns number of cells in simulation """
    dict_dfs = dict()
    if 0 < read_mongo_guaranteed(dictionary=dict_dfs, collection="simulation_configurations"):
        return dict_dfs["simulation_configurations"]["nMacroEnbSites"].iloc[-1] * 3


def update_nb_cell_lists():
    """" Updates neighbouring cell lists in DB. """
    dict_dfs = dict()
    if 0 > read_mongo_guaranteed(dictionary=dict_dfs, collection="handover_log"):
        return
    df_nb_cells = dict()
    read_mongo_guaranteed(dictionary=df_nb_cells, collection="nb_cell_list")

    df_nb_pairs = dict_dfs["handover_log"][["CellID", "TargetCellID"]].loc[dict_dfs["handover_log"]["TargetCellID"] != 0]
    cell_count = get_number_of_cells()

    for i in range(1, cell_count+1):
        new_nb_cells = (df_nb_pairs.loc[(df_nb_pairs["CellID"] == i) | (df_nb_pairs["TargetCellID"] == i)].sum(axis=1) - i).drop_duplicates().tolist()
        if len(df_nb_cells['nb_cell_list']) != 0:
            nb_cells = df_nb_cells['nb_cell_list'].loc[df_nb_cells['nb_cell_list']["CellID"] == i]["NbCellIDs"]
            if len(nb_cells) != 0:
                new_nb_cells.extend(x for x in nb_cells.iloc[0] if x not in new_nb_cells)
        collection_update_with_set(collection="nb_cell_list", query={"CellID": i}, value={"NbCellIDs": new_nb_cells})


##############################################################
#   END: MACHINE LEARNING
##############################################################
