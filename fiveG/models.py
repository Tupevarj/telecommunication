import pandas as pd
from pymongo import MongoClient
from pymongo.database import Database


mongo_conn = MongoClient()
mongo_db = "5gopt"


def connect_to_mongo_db():
    """ A util for making a connection to mongo """
    global mongo_conn
    global mongo_db
    host = "localhost"
    port = 27017
    username = ""
    password = ""
    db = "5gopt"

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        mongo_conn = MongoClient(mongo_uri)
    else:
        mongo_conn = MongoClient(host, port)


# def _connect_mongo():
#     """ A util for making a connection to mongo """
#     host = "localhost"
#     port = 27017
#     username = ""
#     password = ""
#     db = "5gopt"
#
#     if username and password:
#         mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
#         conn = MongoClient(mongo_uri)
#     else:
#         conn = MongoClient(host, port)
#
#     return conn[db]


def get_collection_count(collection):
    global mongo_conn
    global mongo_db
    count = mongo_conn[mongo_db][collection].count()
    return count


def read_collection_as_list_mongo(collection, query={}, skip=0, limit=0):
    """ Returns mongo collection as list """
    global mongo_conn
    global mongo_db

    if not limit == 0:
        col_list = list(mongo_conn[mongo_db][collection].find(query).skip(skip).limit(limit))
    else:
        col_list = list(mongo_conn[mongo_db][collection].find(query).skip(skip))
    return col_list


def collection_read_mongo(collection, query={}, no_id = True, skip=0, limit=0):
    global mongo_conn
    global mongo_db
    cursor = mongo_conn[mongo_db][collection].find(query).skip(skip).limit(limit)
    # TODO: We have to first check the size
    array = list(mongo_conn[mongo_db][collection].find(query).skip(skip).limit(limit))
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
    # db = _connect_mongo()
    global mongo_conn
    global mongo_db
    mongo_conn[mongo_db][collection].insert_one(data)


def calculate_dominatemap_size():
    # db = _connect_mongo()
    global mongo_conn
    global mongo_db
   # db = _connect_mongo()
    # Make a query to the specific DB and Collection
    try:
        return mongo_conn[mongo_db]["dominationmap"].count()
    except:
        return 0










