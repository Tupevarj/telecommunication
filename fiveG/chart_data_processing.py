import pandas as pd
from .models import read_mongo_best_effort, read_mongo_guaranteed, get_collection_count
import json
import numpy as np
import sys

##############################################################
#   PREPROCESS DATA FOR GRAPHS
##############################################################

last_throughput = 0.0
cumulative_throughput = 0
cumulative_rlf_count = 0
prev_thr = 0.0
last_time = 200
prev_time = 200
previous_thr = 0.0
last_read_main = 0
last_read_thr = 0
last_read_dominance = 0
last_read_events = 0
last_read_status = 0
rlf_per_cell = 0
number_of_cells = 0       # MAKE IT READ FROM DATABASE
#last_time_main = 0
#last_time_thr = 0
#last_time_stamp = 0


def get_number_of_cells():
    """ Returns number of cells in simulation """
    dict_dfs = dict()
    if 0 < read_mongo_guaranteed(dictionary=dict_dfs, collection="simulation_configurations"):
        return dict_dfs["simulation_configurations"]["nMacroEnbSites"].iloc[-1] * 3
    else:
        return 0


def init_rlf(): # TODO: Get rid of this!
    global number_of_cells
    global rlf_per_cell
    rlf_per_cell = list()
    for i in range(1, number_of_cells+1):
        rlf_per_cell.append(['Cell ' + str(i), 0])


def initialize_data_processing():
    global prev_thr
    global last_time
    global prev_time
    global last_read_main
    global last_read_thr
    global last_read_dominance
    global last_read_events
    global last_read_status
    global rlf_per_cell
    global cumulative_rlf_count
    global cumulative_throughput
    global last_throughput
    global number_of_cells
   # global last_time_main
   # global last_time_thr
    #global last_time_stamp
    #last_time_stamp = 0

    number_of_cells = get_number_of_cells()
    init_rlf()

    prev_thr = 0.0
    last_time = 200
    prev_time = 200
    last_read_main = 0
    last_read_thr = 0
    last_read_dominance = 0
    last_read_events = 0
    last_read_status = 0
    cumulative_rlf_count = 0
    cumulative_throughput = 0
    last_throughput = 0.0
  #  last_time_main = 0
   # last_time_thr = 0


def update_total_throughput_chart_data(df_throughput, context):
    """ Calculates total throughput at each timestamp.
        Return list of values : [time, value] """
    if len(df_throughput) != 0:
        global last_throughput
        df_data = df_throughput[["Time", "Throughput"]].groupby("Time").sum().reset_index()
        list_throughput = list()
        for row in df_data.itertuples():
            list_throughput.append([row.Time, ((row.Throughput - last_throughput) / (1000000 * 0.2))])
            last_throughput = row.Throughput
        context['TotalThroughput'] = list_throughput


def update_rsrp_per_cell_chart_data(df_data, context):
    """Calculates RSRP for each cell at each timestamp.
        Return dictionary of values : [[Time], [Cell 1], [Cell 2], ...] """
    global number_of_cells
    if len(df_data) != 0:
        dict_chart_data = dict()
        dict_chart_data["Time"] = list(df_data.loc[df_data['CellID'] == 1][["Time", "RSRP"]].groupby("Time").mean().reset_index()["Time"])
        for i in range(1, number_of_cells+1):
            df_cell = df_data.loc[df_data['CellID'] == i][["Time", "RSRP"]].groupby("Time").mean().reset_index()
            if len(df_cell) != 0:
                dict_chart_data["Cell " + str(i)] = list(df_cell["RSRP"])

        context['RSRP'] = dict_chart_data


def update_intialized(context):
    """ Determines if new simulation has been started"""
    global last_read_main
    count_main = get_collection_count(collection="main_kpis_log")
    if last_read_main > count_main:
        context['Initialize'] = json.dumps(True)
        initialize_data_processing()
    else:
        context['Initialize'] = json.dumps(False)


def get_min_squared_distance_index(np_locations, point):
    min_distance = sys.float_info.max
    min_index = 0
    index = 0
    for location in np_locations:
        squared_distance = (location[0] - point[0])**2 + (location[1] - point[1])**2
        if squared_distance < min_distance:
            min_index = index
            min_distance = squared_distance
        index += 1
    return min_index


def update_rlf_per_cell_chart_data(df_events, context):
    if len(df_events) != 0:
        global rlf_per_cell
        np_cell_locations = get_cell_locations()

        np_events = np.array(df_events.loc[df_events['EventID'] == 0][["LocationX", "LocationY"]])
        for point in np_events:
            index = get_min_squared_distance_index(np_cell_locations, point)
            rlf_per_cell[np_cell_locations[index][2]-1][1] += 1
        context['RlfData'] = rlf_per_cell


def update_number_of_users_per_cell_chart_data(df_data, context):
    """ Returns number of connected users per cell latest time stamp """
    if len(df_data) != 0:
        global number_of_cells
        ues_per_cell = list()

        df_connected = df_data.loc[(df_data['CONNECTED']) & (df_data['Time'] == df_data['Time'].iloc[-1])]
        for i in range(1, number_of_cells+1):
            ues_per_cell.append(['Cell ' + str(i), len(df_connected[df_connected["CellID"] == i])])
        context['UesPerCell'] = ues_per_cell


def update_rem_map_chart(df_rem, context):
    """ Saves REM points (pixels) to context parameter """
    if len(df_rem) != 0:
        df_rem['sinr'] = 10 * np.log10(df_rem['sinr'])
        context['DominanceMap'] = df_rem[['x', 'y', 'sinr']].values.tolist()


def get_console_color(type):
    if type == 0:
        return [203, 42, 35]  #"#CB2A23"
    if type == 1:
        return [72, 161, 200]  #"#48a1c8"
    if type == 2:
        return [216, 123, 56]  #"#D87B38"
    if type == 3:
        return [28, 176, 92]  #"#1CB05C"


def update_simulator_status_message_data(status_df, context):
    messages = list()
    for index, row in status_df.iterrows():
        messages.append([row["Time"], row["Message"], get_console_color(row["Type"])])
    context['SimulationStatus'] = messages


def update_latest_rsrp_per_cell_chart_data(df_data, context):
    """ Stores latest RSRP value for each cell into context dictionary """
    global number_of_cells
    if len(df_data) != 0:
        df_latest = df_data[["CellID", "RSRP"]].loc[df_data["Time"] == df_data["Time"].iloc[-1]].groupby("CellID").mean().reset_index()
        list_rsrp = list()
        for cell_id in range(1, number_of_cells+1):
            df_cell = df_latest.loc[df_latest['CellID'] == cell_id]
            if len(df_cell) != 0:
                list_rsrp.append(["Cell "+ str(df_cell["CellID"].values[0]), df_cell["RSRP"].values[0]])
            else:
                list_rsrp.append(["Cell "+ str(cell_id), 0.0])

        context['RsrpPerCell'] = list_rsrp

      #  if len(df_latest) != number_of_cells:
    #        df_latest = df_latest.append(pd.DataFrame(data={"CellID":  [5], "RSRP": [0.0]})).sort_values(by="CellID")
    #    df_latest["CellID"] = 'Cell ' + df_latest['CellID'].astype(str)
  #      context['RsrpPerCell'] = df_latest.values.tolist()


def get_ue_location_and_connection_history(cell_id):
    """ Returns users connection and location history in dictionary """
    # TODO:
    return 0


def get_ue_location_and_connection_history(ue_id):
    """ Returns users connection and location history in dictionary """
    connections_and_locations = dict()
    connections_and_locations["Connections"] = list()
    connections_and_locations["Locations"] = list()
    dict_data_frames = dict()

    length_ho = read_mongo_guaranteed(dictionary=dict_data_frames, collection="handover_log", query={"UserID": ue_id}, skip=0)
    length_main = read_mongo_guaranteed(dictionary=dict_data_frames, collection="main_kpis_log", query={"UserID": ue_id}, skip=0)



    #dict_dfs = read_multiple_mongo_collections_df(collections=["handover_log", "main_kpis_log"], query={"UserID": ue_id}, skips=[0,0])

    if length_ho > 0:
        time_intervals = dict_data_frames["handover_log"][["Time"]].loc[dict_data_frames["handover_log"]['HEventID'] == 1]["Time"].tolist()
        cells = dict_data_frames["handover_log"]["CellID"].loc[dict_data_frames["handover_log"]["CellID"].shift() != dict_data_frames["handover_log"]["CellID"]].tolist()
        connections_and_locations["Connections"] = list(zip([0.4] + time_intervals, time_intervals + [dict_data_frames["main_kpis_log"]["Time"].iloc[-1]], cells))
    elif length_main > 0:
        connections_and_locations["Connections"].append([0.4, dict_data_frames["main_kpis_log"]["Time"].iloc[-1], int(dict_data_frames["main_kpis_log"].loc[dict_data_frames["main_kpis_log"]["CONNECTED"]]["CellID"].iloc[-1])])
    if length_main > 0:
        connections_and_locations["Locations"] = dict_data_frames["main_kpis_log"][["LocationX", "LocationY", "Time"]].loc[dict_data_frames["main_kpis_log"]["CONNECTED"]].values.tolist()

    return connections_and_locations


def get_cell_locations():
    dict_dfs = dict()
    if 0 < read_mongo_guaranteed(dictionary=dict_dfs, collection="cell_configurations"):
        return np.array(dict_dfs["cell_configurations"][["LocationX", "LocationY", "CellID"]].values)


def get_cell_locations_II():
    dict_dfs = dict()
    if 0 < read_mongo_guaranteed(dictionary=dict_dfs, collection="cell_configurations"):
        np_array = np.array(dict_dfs["cell_configurations"][["LocationX", "LocationY"]].values)
        cell_list = np_array.tolist()
        for i in range(0, len(cell_list)):
            cell_list[i] = [cell_list[i][0], cell_list[i][1], ((i+1.0) / 10.0)]
        return cell_list


def update_ac_cumulative_rlf_chart_data(event_df, context):
    """ Returns total count RLF in network (ac)cumulative """
    if len(event_df) != 0:
        global cumulative_rlf_count

        df_counts = event_df[["Time", "EventID"]].loc[event_df['EventID'] == 0].groupby("Time").count().reset_index()
        if len(df_counts) != 0:
            rlf_total = dict()
            rlf_total["Time"] = df_counts["Time"].tolist()
            rlf_total["Accumulative"] = df_counts["EventID"].tolist()
            df_counts["EventID"].iloc[0] += cumulative_rlf_count
            rlf_total["Cumulative"] = df_counts["EventID"].cumsum().tolist()

            cumulative_rlf_count = rlf_total["Cumulative"][-1]
            context['RlfTotal'] = rlf_total


def get_data_for_all_charts(context):
    global last_read_main
    global last_read_thr
    global last_read_events
    global last_read_status
    global last_read_dominance
    global number_of_cells

    if number_of_cells == 0:
        number_of_cells = get_number_of_cells()
        init_rlf()

    # Check if new simulation started and charts need to be initialized
    update_intialized(context)

    # Read collections from mongo:
 #   dict_dfs = read_multiple_mongo_collections_df(collections=["throughput_log", "main_kpis_log", "event_log", "status_log", "rem_log"],
  #                                     skips=[last_read_thr, last_read_main, last_read_events, last_read_status, last_read_dominance])

    data_frames = dict()
    if 0 < read_mongo_best_effort(dictionary=data_frames, collection="throughput_log", skip=last_read_thr):
        last_read_thr += len(data_frames["throughput_log"])
        update_total_throughput_chart_data(data_frames["throughput_log"], context)

    if 0 < read_mongo_best_effort(dictionary=data_frames, collection="main_kpis_log", skip=last_read_main):
        last_read_main += len(data_frames["main_kpis_log"])

        data_frames["main_kpis_log"] = data_frames["main_kpis_log"][np.isfinite(data_frames["main_kpis_log"]['RSRP'])]
        update_rsrp_per_cell_chart_data(data_frames["main_kpis_log"], context)
        update_latest_rsrp_per_cell_chart_data(data_frames["main_kpis_log"], context)
        update_number_of_users_per_cell_chart_data(data_frames["main_kpis_log"], context)

    if 0 < read_mongo_best_effort(dictionary=data_frames, collection="event_log", skip=last_read_events):
        last_read_events += len(data_frames["event_log"])
        update_rlf_per_cell_chart_data(data_frames["event_log"], context)
        update_ac_cumulative_rlf_chart_data(data_frames["event_log"], context)

    if 0 < read_mongo_best_effort(dictionary=data_frames, collection="status_log", skip=last_read_status):
        last_read_status += len(data_frames["status_log"])
        update_simulator_status_message_data(data_frames["status_log"], context)          # TODO

    if 0 < read_mongo_best_effort(dictionary=data_frames, collection="rem_log", skip=last_read_dominance):
        last_read_dominance += len(data_frames["rem_log"])
        update_rem_map_chart(data_frames["rem_log"].tail(22500), context)          # TODO

 #   if len(dict_dfs["main_kpis_log"]) % (105*21) != 0:
 #       errori = True

 #   if len(dict_dfs["throughput_log"]) % (105 * 21) != 0:
 #       errori = True

 #   global last_time_main
  #  global last_time_thr
  #  global last_time_stamp

 #   if len(dict_dfs["throughput_log"]) > 0 and dict_dfs["main_kpis_log"]["Time"].iloc[0] > (last_time_main + 0.25):
  #      errori = True

  #  if len(dict_dfs["main_kpis_log"]) > 0 and dict_dfs["throughput_log"]["Time"].iloc[0] > (last_time_thr + 0.25):
  #      errori = True

  #  if "main_kpis_log" in dict_dfs and len(dict_dfs["main_kpis_log"]) > 0:
  #      last_time_main = dict_dfs["main_kpis_log"]["Time"].iloc[-1]
  #  if "throughput_log" in dict_dfs and len(dict_dfs["throughput_log"]) > 0:
  #      last_time_thr = dict_dfs["throughput_log"]["Time"].iloc[-1]

 #   if "throughput_log" in dict_dfs:
  #      last_read_thr += len(dict_dfs["throughput_log"])
  #      update_total_throughput_chart_data(dict_dfs["throughput_log"], context)

    # if "main_kpis_log" in dict_dfs:
    #
    # if "event_log" in dict_dfs:
    #
    # if "status_log" in dict_dfs:
    #
    # if "rem_log" in dict_dfs:
    #
    # if "throughput_log" in dict_dfs and len(dict_dfs["throughput_log"]) > 0:
    #     time_curr = context['TotalThroughput'][0][0]
    #
    #     if len(dict_dfs["throughput_log"]) > 2:
    #         for i in range(0, len(dict_dfs["throughput_log"])-1):
    #
    #             if dict_dfs["throughput_log"]["Time"][i+1] > (dict_dfs["throughput_log"]["Time"][i] + 0.22):
    #                 ERROR_II = True  # SKIP MUST BE TO BIG???
    #     if time_curr > last_time_stamp + 0.25:
    #         ERROR = True
    #     last_time_stamp = context['TotalThroughput'][-1][0]



