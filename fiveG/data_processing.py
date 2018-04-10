import pandas as pd
from .models import collection_read_mongo
from sklearn import manifold
import numpy as np

##############################################################
#   PREPROCESS DATA FOR GRAPHS
##############################################################

prev_thr = 0.0
last_time = 200
prev_time = 200
previous_thr = 0.0


def initialize_data_processing():
    global prev_thr
    global last_time
    global prev_time
    prev_thr = 0.0
    last_time = 200
    prev_time = 200


def calculate_total_throughput(list_thr):
    """ Calculates total throughput at each timestamp, and stores values
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


def get_rsrp_per_cell_from_collection(list_rsrp, dict_rsrp):
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


##############################################################
#   END: PREPROCESS DATA FOR GRAPHS
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
#   END: OUTPUT TO CSV
##############################################################


##############################################################
#   DATA PREPROCESSING
##############################################################


def preprocess_training_set_to_8_dimensions(dim_8_list, labels, data_frame):
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
            labels.append(numpy_array[0][2])


def preprocess_testing_set_to_10_dimensions(data_frame):
    """ Preprocess data to two arrays, columns:
           -     dim_8_list : RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4
           -   dim_10_list  : Time UserID RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4
           -        array_y : LABEL """

    dim_10_list = list();
    for identity, group in data_frame.groupby(["Time", "UserID"]):
        # Pick the top 4 highest RSRP values and then its corresponding RSRQ values in that row
        numpy_array = np.array(group.values)

        if not np.isnan(numpy_array[0][6]):
            numpy_array = numpy_array[numpy_array[:, 5].argsort()]  # sort

            dim_10_list.append([identity[0], identity[1], numpy_array[0][3], numpy_array[0][4], numpy_array[-1][5], numpy_array[-1][6], numpy_array[-2][5],
                                numpy_array[-2][6], numpy_array[-3][5], numpy_array[-3][6], numpy_array[-4][5],
                                numpy_array[-4][6]])
    return dim_10_list


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


def preprocess_data_8_dim(data):
    """ SHOULD NOT BE USED: ITS SLOW!
        Preprocess data to data frame, columns:
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
    ''' NOT USED ANYMORE?
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
#   END: DATA PREPROCESSING
##############################################################
