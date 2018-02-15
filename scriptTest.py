from pymongo import MongoClient
import pandas as pd
import numpy as np

def _connect_mongo():
    """ A util for making a connection to mongo """
    host = "localhost"
    port = 27017
    username = ""
    password = ""
    db = "5gopt"

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)


    return conn[db]

def collection_read_mongo(collection, query={}, no_id = True):
    db = _connect_mongo()
    cursor = db[collection].find(query)
    df = pd.DataFrame(list(cursor))

    if no_id:
        try:
            del df["_id"]
        except:
            pass
    return df

data = collection_read_mongo(collection="main_file_with_UserTHR")

testData = data[:1000]

wantedDF = pd.DataFrame(columns=["Time", "User", "LocationX", "LocationY", "RSRP_1st", "1stRSRP_Corresponding_RSRQ",
                                 "Serving_Cell","RSRP_2nd", "2ndRSRP_Corresponding_RSRQ", "RSRP_3rd", "3rdRSRP_Corresponding_RSRQ",
                                 "RSRP_4th", "4thRSRP_Corresponding_RSRQ"])
i = 0
jj = 0
for stamp, group in testData.groupby(["Time", "UserID"]):
    #     rsrp_top3 = [0,0,0]
    #     rsrp_matched_record_index = [0, 0,0]
    rsrpIndexList = list()
    for j in range(group.shape[0]):
        rsrpIndexList.append((jj, group["RSRP"][jj]))
        jj += 1
    rsrpIndexListSorted = sorted(rsrpIndexList, key=lambda x: x[1], reverse=True)
    row_rsrp1st = group.loc[rsrpIndexListSorted[0][0]]
    a = row_rsrp1st["Time"]
    b = int(row_rsrp1st["UserID"])
    c = row_rsrp1st["LocationX"]
    d = row_rsrp1st["LocationY"]
    e = row_rsrp1st["RSRP"]
    f = row_rsrp1st["RSRQ"]
    g = int(row_rsrp1st["CellID"])
    h = group.loc[rsrpIndexListSorted[1][0]]["RSRP"]
    p = group.loc[rsrpIndexListSorted[1][0]]["RSRQ"]
    k = group.loc[rsrpIndexListSorted[2][0]]["RSRP"]
    l = group.loc[rsrpIndexListSorted[2][0]]["RSRQ"]
    m = group.loc[rsrpIndexListSorted[3][0]]["RSRP"]
    n = group.loc[rsrpIndexListSorted[3][0]]["RSRQ"]
    # wantedDF.append([{"Time": a, "User": b, "LocationX": c, "LocationY": d, "RSRP_1st": e, "1stRSRP_Corresponding_RSRQ": f,
    #                 "Serving_Cell": g,"RSRP_2nd":h, "2ndRSRP_Corresponding_RSRQ": p, "RSRP_3rd": k, "3rdRSRP_Corresponding_RSRQ":l,
    #                              "RSRP_4th":m, "4thRSRP_Corresponding_RSRQ": n}], ignore_index=True)
    wantedDF.loc[i] = [a, b, c, d, e, f, g, h, p, k, l, m, n]
    i += 1


# apply machine learning algorithm
j = 0
