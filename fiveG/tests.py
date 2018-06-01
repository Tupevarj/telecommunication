# import sys
# import numpy as np
# import pandas as pd
# from numpy import genfromtxt
#
#
# def preprocess_training_set_to_13_dimensions(data_frame):
#     """ Preprocess data to two arrays, columns:
#            -     dim_8_list : RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4
#            -   dim_10_list  : Time UserID RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4
#            -        array_y : LABEL """
#     dim_13_list = list()
#     for identity, group in data_frame.groupby(["Time", "UserID"]):
#         # Pick the top 4 highest RSRP values and then its corresponding RSRQ values in that row
#         if not bool(pd.isnull(group.values).any()):
#             numpy_array = np.array(group.values)
#             numpy_array = numpy_array[numpy_array[:, 5].argsort()]  # sort
#
#             dim_13_list.append([identity[0], identity[1], numpy_array[0][1], numpy_array[0][2], numpy_array[-1][5],
#                                 numpy_array[-1][6], numpy_array[-2][5],numpy_array[-2][6], numpy_array[-3][5],
#                                 numpy_array[-3][6], numpy_array[-4][5],numpy_array[-4][6], numpy_array[0][8]])
#     return dim_13_list
#
#
# def write_np_array_to_csv_file(np_array, output):
#     """ Writes dataframe to CSV file"""
#     file = open(output, 'w')
#     file.write("Time,UserID,LocationX,LocationY,RSRP1,RSRQ1,RSRP2,RSRQ2,RSRP3,RSRQ3,RSRP4,RSRQ4,LABEL\n")
#
#     for row_i in range(0, len(np_array)):
#         comma = ""
#         for col_i in range(0, len(np_array[row_i])):
#             file.write(comma + str(np_array[row_i][col_i]))
#             comma = ","
#         file.write("\n")
#     file.close()
#
#
# def preprocessed_data_to_csv_file(data, output):
#     """ Save preprocessed 13 dimensional data into CSV file """
#     col_names = ["Time", "LocationX", "LocationY", "UserID", "CellID", "RSRP", "RSRQ", "CONNECTED", "LABEL"]
#     data = pd.read_csv(data, names=col_names)
#
#     processed = preprocess_training_set_to_13_dimensions(data)
#     write_np_array_to_csv_file(np_array=processed, output=output)
#
#
#
# preprocessed_data_to_csv_file("/home/tupevarj/NS3SimulatorData/DATASETS/data_set_1/main_log_with_labels.csv", "./testi2.csv")
