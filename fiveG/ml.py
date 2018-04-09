'''
this file deals with data analysis
'''
import pandas as pd
import numpy as np
from .models import collection_read_mongo
from sklearn import manifold
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

class Regressor(Enum):
    SIMPLE_REG = 0
    DECISION_TREE_REG = 1
    RANDOM_FOREST_REG = 2
    SVR_REG = 3


sel_reg_enum = Regressor.SIMPLE_REG
regressors_chart_data = [0, 0, 0, 0]
regressors_table_data = [0, 0, 0, 0]
z_scores_ref = [0, 0, 0, 0]
regressors = [LinearRegression(), DecisionTreeRegressor(random_state=0), RandomForestRegressor(n_estimators=10, random_state=0),
              SVR(kernel='rbf')]


def get_ref_z_scores(reg_enum):
    """ Return reference Z-scores based on enum value."""
    global z_scores_ref
    return z_scores_ref[reg_enum.value]


def get_regressor(reg_enum):
    """ Return regressor based on enum value. NOT NEEDED ANY LONGER!"""
    global regressors
    return regressors[reg_enum.value]


#######################################
#   TRAIN REGRESSORS
#######################################

def train_simple_regressor(x_train, y_train):
    """ Train simple regressor """
    global regressors
    regressors[Regressor.SIMPLE_REG.value].fit(x_train, y_train)


def train_decision_tree_regressor(x_train, y_train):
    """ Train decision tree regressor """
    global regressors
    regressors[Regressor.DECISION_TREE_REG.value].fit(x_train, y_train)


def train_random_forest_regressor(x_train, y_train):
    """ Train random forest regressor """
    global regressors
    regressors[Regressor.RANDOM_FOREST_REG.value].fit(x_train, y_train)


def train_svr_regressor(x_train, y_train):
    """ Train svr regressor """
    global regressors
    regressors[Regressor.SVR_REG.value].fit(x_train, y_train)


#######################################
#   TEST REGRESSORS
#######################################

def test_regressor(regressor, test_data, correct_answers, points):
    """ Test regressor with test set and correct answers
        Returns Area Under the Curve (AUC)
        Also writes points for graph in points parameter"""
    predictions = cross_val_predict(regressor, test_data, correct_answers, cv=6)
    false_positive_rate, true_positive_rate, thresholds = roc_curve(correct_answers, predictions)

    points.append(zip(false_positive_rate, true_positive_rate))
    return auc(false_positive_rate, true_positive_rate)


def test_simple_regressor(x_test, actual, points):
    """ Test simple regressor with test set and correct answers
        Returns Area Under the Curve (AUC)
        Also writes points for graph in points parameter"""
    global regressors
    return test_regressor(regressors[Regressor.SIMPLE_REG.value], x_test, actual, points)


def test_decision_tree_regressor(x_test, actual, points):
    """ Test decision tree regressor with test set and correct answers
        Returns Area Under the Curve (AUC)
        Also writes points for graph in points parameter"""
    global regressors
    return test_regressor(regressors[Regressor.DECISION_TREE_REG.value], x_test, actual, points)


def test_random_forest_regressor(x_test, actual, points):
    """ Test random forest regressor with test set and correct answers
        Returns Area Under the Curve (AUC)
        Also writes points for graph in points parameter"""
    global regressors
    return test_regressor(regressors[Regressor.RANDOM_FOREST_REG.value], x_test, actual, points)


def test_svr_regressor(x_test, actual, points):
    """ Test SVR regressor with test set and correct answers
        Returns Area Under the Curve (AUC)
        Also writes points for graph in points parameter"""
    global regressors
    return test_regressor(regressors[Regressor.SVR_REG.value], x_test, actual, points)


def preprocess_training_set_to_8_and_10_dimensions(dim_8_list, dim_10_list, labels, data_frame):
    """ Preprocess data to two arrays, columns:
           -     dim_8_list : RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4
           -   dim_10_list  : Time UserID RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4
           -        array_y : LABEL """

    for identity, group in data_frame.groupby(["Time", "UserID"]):
        # Pick the top 4 highest RSRP values and then its corresponding RSRQ values in that row
        numpy_array = np.array(group.values)

        if not np.isnan(numpy_array[0][6]):
            numpy_array = numpy_array[numpy_array[:, 5].argsort()]  # sort
            dim_8_list.append([numpy_array[-1][5], numpy_array[-1][6], numpy_array[-2][5], numpy_array[-2][6],
                               numpy_array[-3][5], numpy_array[-3][6], numpy_array[-4][5], numpy_array[-4][6]])

            dim_10_list.append([identity[0], identity[1], numpy_array[0][3], numpy_array[0][4], numpy_array[-1][5], numpy_array[-1][6], numpy_array[-2][5],
                                numpy_array[-2][6], numpy_array[-3][5], numpy_array[-3][6], numpy_array[-4][5],
                                numpy_array[-4][6]])

            labels.append(numpy_array[0][2])


def load_all_regressors():
    """ Load all previously save regressors from hard drive"""
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

        z_scores_ref = (np.array(z_scores)).tolist()

        regressors_table_data[Regressor.SIMPLE_REG.value] = auc_data.iloc[0][0]
        regressors_table_data[Regressor.DECISION_TREE_REG.value] = auc_data.iloc[0][1]
        regressors_table_data[Regressor.RANDOM_FOREST_REG.value] = auc_data.iloc[0][2]
        regressors_table_data[Regressor.SVR_REG.value] = auc_data.iloc[0][3]

        training_done = True

        return 1
        #return points
    except:
        return 0


def write_xy_to_csv_file(list_xy, file_name):
    """ Writes list of tuples to CSV file """
    file = open(file_name, 'w')
    file.write("X,Y\n")
    for i in range(0, len(list_xy)):
        file.write(str(list_xy[i][0]) + "," + str(list_xy[i][1]) + "\n")
    file.close()


def set_regressor(reg_enum):
    """ Sets current regressor """
    global sel_reg_enum
    sel_reg_enum = Regressor(reg_enum)


def save_all_regressors():
    """ Save all trained regressors to hard drive"""
   # global training_done
    #if training_done:
    global regressors
    global regressors_chart_data
    global regressors_table_data

    # Save regressors
    joblib.dump(regressors[Regressor.SIMPLE_REG.value], 'simple_reg.pkl')
    joblib.dump(regressors[Regressor.DECISION_TREE_REG.value], 'dt_reg.pkl')
    joblib.dump(regressors[Regressor.RANDOM_FOREST_REG.value], 'rf_reg.pkl')
    joblib.dump(regressors[Regressor.SVR_REG.value], 'svr_reg.pkl')

    # Save performance of regressors
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
        for j in range(0, len(z_scores_ref[i])):
            file.write(comma + str(z_scores_ref[i][j]))
            comma = ","
        file.write("\n")
    file.close()
    return 1


def get_reg_chart_data():
    global regressors_chart_data
    return regressors_chart_data


def get_auc_scores():
    global regressors_table_data
    return regressors_table_data


def get_reg_z_scores():
    global z_scores_ref
    return z_scores_ref


def get_current_z_scores():
    global sel_reg_enum
    return z_scores_ref[sel_reg_enum.value]


def do_all_regressions(array_x, array_y):
    """ Get points and auc values for each classifier """
    global training_done
    global regressors_chart_data
    global regressors_table_data
    points = list()
    # split the data:
    x_train, x_test, y_train, y_test = train_test_split(array_x, array_y, test_size=0.2, random_state=7)

    # Simple regressor
    train_simple_regressor(x_train=x_train, y_train=y_train)
    regressors_table_data[Regressor.SIMPLE_REG.value] = test_simple_regressor(x_test=x_test, actual=y_test, points=points)

    # Decision tree regressor
    train_decision_tree_regressor(x_train=x_train, y_train=y_train)
    regressors_table_data[Regressor.DECISION_TREE_REG.value] = test_decision_tree_regressor(x_test=x_test, actual=y_test, points=points)

    # Random forest regressor
    train_random_forest_regressor(x_train=x_train, y_train=y_train)
    regressors_table_data[Regressor.RANDOM_FOREST_REG.value] = test_random_forest_regressor(x_test=x_test, actual=y_test, points=points)

    # SVR regressor
    train_svr_regressor(x_train=x_train, y_train=y_train)
    regressors_table_data[Regressor.SVR_REG.value] = test_svr_regressor(x_test=x_test, actual=y_test, points=points)

    training_done = True
    regressors_chart_data[Regressor.SIMPLE_REG.value] = list(points[0])
    regressors_chart_data[Regressor.DECISION_TREE_REG.value] = list(points[1])
    regressors_chart_data[Regressor.RANDOM_FOREST_REG.value] = list(points[2])
    regressors_chart_data[Regressor.SVR_REG.value] = list(points[3])


def calculate_z_scores(predictions, x_test):
    """ Calculates z-scores based on predictions from regressor,
        also needs to have data containing user locations"""
    dataset_basestations = pd.read_csv("/home/tupevarj/Desktop/basestations.csv")  # TODO: make it read from DB

    dict_users_per_bs = dict()
    for i in range(0, 7):
        dict_users_per_bs["BS" + str(i + 1)] = 0

    for i in range(0, len(predictions)):
        if predictions[i] >= 0.1:
            ue_location = [x_test[i][2], x_test[i][3]]
            # Calculate min distance:
            min_distance = sys.float_info.max
            base_station_id = -1
            for j, bs in dataset_basestations.iterrows():
                distance = math.sqrt(((bs["LocationX"] - ue_location[0]) ** 2) + ((bs["LocationY"] - ue_location[1]) ** 2))
                if distance < min_distance:
                    min_distance = distance
                    base_station_id = j + 1

            key = "BS" + str(base_station_id)
            dict_users_per_bs[key] += 1

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


def do_calculate_z_scores(array_x, array_y):
    """ Calculates z-score for regressor
        TODO: change the way that user decides which regressor to use"""
    global regressors
    global z_scores_ref
    x_train, x_test, y_train, y_test = train_test_split(array_x, array_y, test_size=0.2, random_state=7)
    predictions = regressors[Regressor.SIMPLE_REG.value].predict(np.asarray(x_test)[:, 4:])
    z_scores_ref[Regressor.SIMPLE_REG.value] = calculate_z_scores(predictions, x_test)
    predictions = regressors[Regressor.DECISION_TREE_REG.value].predict(np.asarray(x_test)[:, 4:])
    z_scores_ref[Regressor.DECISION_TREE_REG.value] = calculate_z_scores(predictions, x_test)
    predictions = regressors[Regressor.RANDOM_FOREST_REG.value].predict(np.asarray(x_test)[:, 4:])
    z_scores_ref[Regressor.RANDOM_FOREST_REG.value] = calculate_z_scores(predictions, x_test)
    predictions = regressors[Regressor.SVR_REG.value].predict(np.asarray(x_test)[:, 4:])
    z_scores_ref[Regressor.SVR_REG.value] = calculate_z_scores(predictions, x_test)
    return z_scores_ref


def run_ml(array_x):
    """ Run machine learning once. Returns ID of broken cell.
        Based on comparing reference and new z-scores """
    #global z_scores_ref
    #global training_done
    global sel_reg_enum
  #  if not training_done:
   #     return -1
    regressor = get_regressor(sel_reg_enum)
    predictions = regressor.predict(np.asarray(array_x)[:, 4:])
    z_score_ref = get_ref_z_scores(sel_reg_enum)
    z_scores_new = calculate_z_scores(predictions, array_x)

    #highest_z_score = -1
    #outage_id = 0

    high4 = [0, -1]
    for i in range(0, 7):
        if high4[1] < z_scores_new[i]:
            high4[1] = z_scores_new[i]
            high4[0] = i + 1
            #high4[2] = z_scores_new[i]
            score_outage = []
    for i in range(0, 7):
       # if i == 3 and z_scores_new[i] == high4[1]:
       #     score_outage.append(i)
        if z_scores_new[i] >= z_score_ref[i]:
            score_outage.append(i)
            maxval = [0, -1]

    for i in range(0, len(score_outage)):
        if maxval[1] < z_scores_new[score_outage[i]]:
            maxval[1] = z_scores_new[score_outage[i]]
            maxval[0] = score_outage[i] + 1
            #maxval[2] = z_scores_new[score_outage[i]]

    if maxval[1] >= 2:
        return [maxval[0], z_scores_new]
    else:
        return [0, z_scores_new]

    # OLD CODE
    # for i in range(0, 7):
    #     if z_scores_new[i] >= z_scores_ref[i] and z_scores_new[i] > highest_z_score:
    #         outage_id = i +1
    #         highest_z_score = z_scores_new[i]


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


##############################################################
#   END: NOT USED FUNCTIONS AND VARIABLES
##############################################################
