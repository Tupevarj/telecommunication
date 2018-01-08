import pandas as pd
from pymongo import MongoClient


def preProcess():
    normalDF = pd.DataFrame(columns=["Time", "UeNodeNo", "UeRNTI", "Cell_ID", "RSRP", "Serving_Cell"])

    index = 0
    for doc in normal.objects[:1000]:
        normalDF.loc[index] = [doc.Time, doc.UeNodeNo, doc.UeRNTI, doc.Cell_ID, doc.RSRP, doc.Serving_Cell]
        index = index + 1
    print("finish load")
    return normalDF



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


def normalCol_read_mongo(query={}, no_id=True):
    """ Read from Mongo and Store into DataFrame """
    collection = "normal"
    # Connect to MongoDB
    db = _connect_mongo()
    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)
    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        try:
            del df['_id']
        except:
            pass
    return df

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


def insert_document(collection, data):
    db = _connect_mongo()
    db[collection].insert_one(data)


def calculate_dominatemap_size():
    db = _connect_mongo()
    # Make a query to the specific DB and Collection
    try:
        return db["dominationmap"].count()
    except:
        return 0










