import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn import manifold


def preprocess_training_set_to_10_dimensions(data_frame):
    """ Preprocess data to two arrays, columns:
           -     dim_10_list : RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4 RSRP_5 RSRQ_5 """
    dim_8_list = list()
    for identity, group in data_frame.groupby(["Time", "UserID"]):
        # Pick the top 4 highest RSRP values and then its corresponding RSRQ values in that row
        if not bool(pd.isnull(group.values).any()):
            numpy_array = np.array(group.values)
            numpy_array = numpy_array[numpy_array[:, 5].argsort()]  # sort

            dim_8_list.append([numpy_array[-1][5],
                                numpy_array[-1][6], numpy_array[-2][5], numpy_array[-2][6], numpy_array[-3][5],
                                numpy_array[-3][6], numpy_array[-4][5], numpy_array[-4][6], numpy_array[-5][5],
                                numpy_array[-5][6]])
    return dim_8_list


def preprocess_training_set_to_8_dimensions(data_frame):
    """ Preprocess data to two arrays, columns:
           -     dim_8_list : RSRP_1 RSRQ_1 RSRP_2 RSRQ_2 RSRP_3 RSRQ_3 RSRP_4 RSRQ_4 """
    dim_8_list = list()
    for identity, group in data_frame.groupby(["Time", "UserID"]):
        # Pick the top 4 highest RSRP values and then its corresponding RSRQ values in that row
        if not bool(pd.isnull(group.values).any()):
            numpy_array = np.array(group.values)
            numpy_array = numpy_array[numpy_array[:, 5].argsort()]  # sort

            dim_8_list.append([numpy_array[-1][5],
                                numpy_array[-1][6], numpy_array[-2][5], numpy_array[-2][6], numpy_array[-3][5],
                                numpy_array[-3][6], numpy_array[-4][5], numpy_array[-4][6]]) #, int(numpy_array[0][8])])
    return dim_8_list


CREATE_MDS_CHARTS = False
CREATE_RSRP_CHARTS = False
CREATE_RLF_CHARTS = False
CREATE_RLF_COMPARISON = True

# -------------------------------------------------------------------------------
#       MDS
# -------------------------------------------------------------------------------

if CREATE_MDS_CHARTS:
    col_names = ["Time", "LocationX", "LocationY", "UserID", "CellID", "RSRP", "RSRQ", "CONNECTED", "LABEL"]
    df = pd.read_csv("/home/tupevarj/NS3SimulatorData/Testing/main_log_with_labels.csv", names=col_names)

    normal_rows = df.loc[(df['LABEL'] == 0)]
    anomaly_rows = df.loc[(df['LABEL'] == 1)]

    processed_n = preprocess_training_set_to_8_dimensions(normal_rows)
    processed_a = preprocess_training_set_to_8_dimensions(anomaly_rows)

    mds = manifold.MDS(3, max_iter=5000, n_init=4)
    three_dim_n = mds.fit_transform(processed_n[:1000])
    three_dim_a = mds.fit_transform(processed_a)
    df_3_n = pd.DataFrame(three_dim_n)
    df_3_a = pd.DataFrame(three_dim_a)

    normal_dim_1 = list()
    normal_dim_2 = list()
    anomaly_dim_1 = list()
    anomaly_dim_2 = list()


    for index, row in df_3_n.iterrows():
        normal_dim_1.append(row.iloc[0])
        normal_dim_2.append(row.iloc[1])

    for index, row in df_3_a.iterrows():
        anomaly_dim_1.append(row.iloc[0])
        anomaly_dim_2.append(row.iloc[1])

    plt.xlabel('MDS 1')
    plt.ylabel('MDS 2')
    plt.plot(normal_dim_1, normal_dim_2, 'bo')
    plt.plot(anomaly_dim_1, anomaly_dim_2, 'ro')
    #plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot_MDS.png")
    plt.show()


# -------------------------------------------------------------------------------


if CREATE_RSRP_CHARTS:
    folder = "new"

    df = pd.read_csv("/home/tupevarj/NS3SimulatorData/Testing/new_8.csv")

    normal_rows = df.loc[(df['LABEL'] == 0)]
    anomaly_rows = df.loc[(df['LABEL'] == 1)]

    normal_loc_x = list()
    normal_loc_y = list()
    anomaly_loc_x = list()
    anomaly_loc_y = list()

    for index, row in normal_rows.iterrows():
        normal_loc_x.append(row['LocationX'])
        normal_loc_y.append(row['LocationY'])

    for index, row in anomaly_rows.iterrows():
        anomaly_loc_x.append(row['LocationX'])
        anomaly_loc_y.append(row['LocationY'])

    plt.xlabel('Location X')
    plt.ylabel('Location Y')
    plt.plot(normal_loc_x, normal_loc_y, 'bo')
    plt.plot(anomaly_loc_x, anomaly_loc_y, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot0.png")
    plt.show()

    normal_rsrp_4 = list()
    normal_rsrp_3 = list()
    normal_rsrp_2 = list()
    normal_rsrp_1 = list()
    anomaly_rsrp_4 = list()
    anomaly_rsrp_3 = list()
    anomaly_rsrp_2 = list()
    anomaly_rsrp_1 = list()

    for index, row in normal_rows.iterrows():
        normal_rsrp_1.append(row['RSRP1'])
        normal_rsrp_2.append(row['RSRP2'])
        normal_rsrp_3.append(row['RSRP3'])
        normal_rsrp_4.append(row['RSRP4'])

    for index, row in anomaly_rows.iterrows():
        anomaly_rsrp_1.append(row['RSRP1'])
        anomaly_rsrp_2.append(row['RSRP2'])
        anomaly_rsrp_3.append(row['RSRP3'])
        anomaly_rsrp_4.append(row['RSRP4'])


    plt.xlabel('RSRP 1')
    plt.ylabel('RSRP 2')
    plt.plot(normal_rsrp_1, normal_rsrp_2, 'bo')
    plt.plot(anomaly_rsrp_1, anomaly_rsrp_2, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot1.png")
    plt.show()

    plt.xlabel('RSRP 1')
    plt.ylabel('RSRP 3')
    plt.plot(normal_rsrp_1, normal_rsrp_3, 'bo')
    plt.plot(anomaly_rsrp_1, anomaly_rsrp_3, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot2.png")
    plt.show()

    plt.xlabel('RSRP 1')
    plt.ylabel('RSRP 4')
    plt.plot(normal_rsrp_1, normal_rsrp_4, 'bo')
    plt.plot(anomaly_rsrp_1, anomaly_rsrp_4, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot3.png")
    plt.show()


    plt.xlabel('RSRP 2')
    plt.ylabel('RSRP 1')
    plt.plot(normal_rsrp_2, normal_rsrp_1, 'bo')
    plt.plot(anomaly_rsrp_2, anomaly_rsrp_1, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot4.png")
    plt.show()


    plt.xlabel('RSRP 2')
    plt.ylabel('RSRP 3')
    plt.plot(normal_rsrp_2, normal_rsrp_3, 'bo')
    plt.plot(anomaly_rsrp_2, anomaly_rsrp_3, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot5.png")
    plt.show()


    plt.xlabel('RSRP 2')
    plt.ylabel('RSRP 4')
    plt.plot(normal_rsrp_2, normal_rsrp_4, 'bo')
    plt.plot(anomaly_rsrp_2, anomaly_rsrp_4, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot6.png")
    plt.show()


    plt.xlabel('RSRP 3')
    plt.ylabel('RSRP 1')
    plt.plot(normal_rsrp_3, normal_rsrp_1, 'bo')
    plt.plot(anomaly_rsrp_3, anomaly_rsrp_1, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot7.png")
    plt.show()

    plt.xlabel('RSRP 3')
    plt.ylabel('RSRP 2')
    plt.plot(normal_rsrp_3, normal_rsrp_2, 'bo')
    plt.plot(anomaly_rsrp_3, anomaly_rsrp_2, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot8.png")
    plt.show()

    plt.xlabel('RSRP 3')
    plt.ylabel('RSRP 4')
    plt.plot(normal_rsrp_3, normal_rsrp_4, 'bo')
    plt.plot(anomaly_rsrp_3, anomaly_rsrp_4, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot9.png")
    plt.show()


    plt.xlabel('RSRP 4')
    plt.ylabel('RSRP 1')
    plt.plot(normal_rsrp_4, normal_rsrp_1, 'bo')
    plt.plot(anomaly_rsrp_4, anomaly_rsrp_1, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot10.png")
    plt.show()

    plt.xlabel('RSRP 4')
    plt.ylabel('RSRP 2')
    plt.plot(normal_rsrp_4, normal_rsrp_2, 'bo')
    plt.plot(anomaly_rsrp_4, anomaly_rsrp_2, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot11.png")
    plt.show()

    plt.xlabel('RSRP 4')
    plt.ylabel('RSRP 3')
    plt.plot(normal_rsrp_4, normal_rsrp_3, 'bo')
    plt.plot(anomaly_rsrp_4, anomaly_rsrp_3, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot12.png")
    plt.show()


    plt.xlabel('RSRP 1')
    plt.ylabel('RSRP 1')
    plt.plot(normal_rsrp_1, normal_rsrp_1, 'bo')
    plt.plot(anomaly_rsrp_1, anomaly_rsrp_1, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot13.png")
    plt.show()


    plt.xlabel('RSRP 2')
    plt.ylabel('RSRP 2')
    plt.plot(normal_rsrp_2, normal_rsrp_2, 'bo')
    plt.plot(anomaly_rsrp_2, anomaly_rsrp_2, 'ro')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/" + folder + "/plot14.png")
    plt.show()


if CREATE_RLF_COMPARISON:
    df_40 = pd.read_csv("/home/tupevarj/NS3SimulatorData/Testing/500_40_support_RLF_25_50/event_log.csv",
                            names=["Time", "LocationX", "LocationY", "UserID", "EventID", "CellID", "RSRP"])
    rlf_rows_40 = df_40.loc[df_40['EventID'] == 0]

    df_43 = pd.read_csv("/home/tupevarj/NS3SimulatorData/Testing/500_43_support_RLF_25_50/event_log.csv",
                        names=["Time", "LocationX", "LocationY", "UserID", "EventID", "CellID", "RSRP"])
    rlf_rows_43 = df_43.loc[df_43['EventID'] == 0]

    df_46 = pd.read_csv("/home/tupevarj/NS3SimulatorData/Testing/500_46_support_RLF_25_50/event_log.csv",
                        names=["Time", "LocationX", "LocationY", "UserID", "EventID", "CellID", "RSRP"])
    rlf_rows_46 = df_46.loc[df_46['EventID'] == 0]

    x_axis = []
    y_axis_40 = []
    y_axis_43 = []
    y_axis_46 = []
    x_axis.append(0)
    y_axis_40.append(0)
    y_axis_43.append(0)
    y_axis_46.append(0)

    for index, row in rlf_rows_40.iterrows():
        y_axis_40[0] += 1

    for index, row in rlf_rows_43.iterrows():
        y_axis_43[0] += 1

    for index, row in rlf_rows_46.iterrows():
        y_axis_46[0] += 1

        # create plot
    fig, ax = plt.subplots()
    # index = np.arange(n_groups)
    bar_width = 0.05
    margin = 0.05
    opacity = 0.8

    x_np = np.array(x_axis)

    rects1 = plt.bar(x_np, y_axis_40, bar_width,
                     alpha=opacity,
                     color='r',
                     label='Tx 40')

    rects2 = plt.bar(x_np + margin + bar_width, y_axis_43, bar_width,
                     alpha=opacity,
                     color='b',
                     label='Tx 43')

    rects3 = plt.bar(x_np + margin + bar_width + margin + bar_width, y_axis_46, bar_width,
                     alpha=opacity,
                     color='g',
                     label='Tx 46')

    plt.xlabel('Transmission Power')
    plt.ylabel('RLF count')
    plt.title('RLF for different transmission powers')
    plt.xticks(x_np + bar_width, x_np)
    plt.legend()

    plt.tight_layout()
    plt.savefig("/home/tupevarj/Downloads/PLOTS/RLF_COMPARISON.png")
    plt.show()

    i = 0

if CREATE_RLF_CHARTS:

    ################################################################
    #   RLFs per cell
    ################################################################

    df_events = pd.read_csv("/home/tupevarj/NS3SimulatorData/Testing/event_log.csv",
                            names=["Time", "LocationX", "LocationY", "UserID", "EventID", "CellID", "RSRP"])
    rlf_rows = df_events.loc[df_events['EventID'] == 0]

    x_axis = []
    y_normal = []
    y_outage = []

    y_axis = []
    for i in range(0, 57):
        x_axis.append(i+1)
        y_axis.append(0)
        y_normal.append(0)
        y_outage.append(0)

    for index, row in rlf_rows.iterrows():
        y_axis[int(row["CellID"])-1] += 1
        if row["Time"] < 10.0:
            y_normal[int(row["CellID"])-1] += 1
        else:
            y_outage[int(row["CellID"])-1] += 1

    plt.xlabel('Cell ID')
    plt.ylabel('RLF count')

    plt.bar(x_axis, y_axis, 1/1.5, color="blue")
    plt.savefig("/home/tupevarj/Downloads/PLOTS/RLF_213.png")
    plt.show()

    ################################################################
    #   RLFs in normal and outage scenario
    ################################################################

    #n_groups = 22

    x_np = np.array(x_axis)

    # create plot
    fig, ax = plt.subplots()
   # index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    rects1 = plt.bar(x_np, y_normal, bar_width,
                     alpha=opacity,
                     color='b',
                     label='Normal')

    rects2 = plt.bar(x_np + bar_width, y_outage, bar_width,
                     alpha=opacity,
                     color='g',
                     label='Outage')

    plt.xlabel('Cell ID')
    plt.ylabel('RLF count')
    plt.title('RLF for Cells')
    plt.xticks(x_np + bar_width, x_np)
    plt.legend()

    plt.tight_layout()
    plt.savefig("/home/tupevarj/Downloads/PLOTS/RLF_COM46.png")
    plt.show()

    ################################################################
    #   RLF Locations
    ################################################################

    x_rlf_loc = []
    y_rlf_loc = []

    for index, row in rlf_rows.iterrows():
        x_rlf_loc.append(row['LocationX'])
        y_rlf_loc.append(row['LocationY'])

    plt.xlabel('Location X')
    plt.ylabel('Location Y')
    plt.plot(x_rlf_loc, y_rlf_loc, 'bo')
    plt.savefig("/home/tupevarj/Downloads/PLOTS/RLF_LOC_4123.png")
    plt.show()
