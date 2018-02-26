import pandas as pd
from pymongo import MongoClient


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
    """ Connect to MongoDB, Read from Mongo and Store into DataFrame """
    db = _connect_mongo()
    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)
    # Expand the cursor and construct the DataFrame
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










