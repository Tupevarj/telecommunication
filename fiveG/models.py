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

def get_collection_count(collection):
    db = _connect_mongo()       # TODO: SHOULD ONLY BE DONE ONCE????
    count = db[collection].count()
    return count


def read_collection_as_list_mongo(collection, query={}, skip=0):
    db = _connect_mongo()       # TODO: SHOULD ONLY BE DONE ONCE????
    col_list = list(db[collection].find(query).skip(skip))
    return col_list


def collection_read_mongo(collection, query={}, no_id = True, skip=0):
    db = _connect_mongo()       # TODO: SHOULD ONLY BE DONE ONCE????
    cursor = db[collection].find(query).skip(skip)
    # TODO: We have to first check the size
    array = list(db[collection].find(query).skip(skip))
    df = pd.DataFrame(list(cursor))

    x = []
    for i in array:
        x.append(i)

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










