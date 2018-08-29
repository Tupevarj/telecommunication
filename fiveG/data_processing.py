import pandas as pd
from .models import read_mongo_guaranteed
import numpy as np

##############################################################
#   OUTPUT TO CSV
##############################################################


def preprocessed_data_to_csv_file(path):
    """ Save preprocessed 8 dimensional data to CSV file and labels to another"""
    file = open(path + "simulation_data.csv", 'a')
    file_labels = open(path + "simulation_data_labels.csv", 'a')
    file.write("Time,UserID,LocationX,LocationY,RSRP1,RSRQ1,RSRP2,RSRQ2,RSRP3,RSRQ3,RSRP4,RSRQ4\n")
    file_labels.write("Label\n")
    file.close()
    file_labels.close()

    dict_dfs = dict()
    if 0 < read_mongo_guaranteed(dictionary=dict_dfs, collection="main_kpis_log"):
        processed = preprocess_data_8_dim(dict_dfs["main_kpis_log"])
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


def preprocess_cod_train(data_frame):
    """ Preprocess data to two arrays, columns:
           -     dim_8_list : RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4
           -      locations : LocationX, LocationY
           -        array_y : LABEL """

    storage = dict()
    storage['data'] = list()
    storage['labels'] = list()

    for identity, group in data_frame.groupby(["Time", "UserID"]):
        # Pick the top 4 highest RSRP values and then its corresponding RSRQ values in that row
        numpy_array = np.array(group.values)

        if not np.isnan(numpy_array[0][6]):
            numpy_array = numpy_array[numpy_array[:, 5].argsort()]  # sort
            storage['data'].append([numpy_array[0][3], numpy_array[0][4], numpy_array[-1][5], numpy_array[-1][6], numpy_array[-2][5], numpy_array[-2][6],
                               numpy_array[-3][5], numpy_array[-3][6], numpy_array[-4][5], numpy_array[-4][6]])
           # locations = np.append(locations, [numpy_array[0][3], numpy_array[0][4]])
            storage['labels'].append(numpy_array[0][2])
    storage['data'] = np.asarray(storage['data'])
    storage['labels'] = np.asarray(storage['labels'])
    return storage


def preprocess_cod(data, locations, data_frame):
    """ Preprocess data to two arrays, columns:
           -     dim_8_list : RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4
           -      locations : LocationX, LocationY
           -        array_y : LABEL """

    for identity, group in data_frame.groupby(["Time", "UserID"]):
        # Pick the top 4 highest RSRP values and then its corresponding RSRQ values in that row
        numpy_array = np.array(group.values)

        if not np.isnan(numpy_array[0][6]):
            numpy_array = numpy_array[numpy_array[:, 5].argsort()]  # sort
            data = np.append(data, [numpy_array[-1][5], numpy_array[-1][6], numpy_array[-2][5], numpy_array[-2][6],
                               numpy_array[-3][5], numpy_array[-3][6], numpy_array[-4][5], numpy_array[-4][6]])
            locations = np.append(locations, [numpy_array[0][3], numpy_array[0][4]])


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

    dim_10_list = list()
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


##############################################################
#   END: DATA PREPROCESSING
##############################################################
