import pandas as pd
import pymongo
from pymongo import MongoClient
from pymongo.database import Database
import time
import calendar
import heapq
import subprocess
from threading import Thread
import numpy as np

mongo_conn = MongoClient()
mongo_db = "5gopt"


def start_mongo():
    subprocess.call(["./start_mongo.sh"])


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
        try:
            mongo_conn = MongoClient(host, port, serverSelectionTimeoutMS=2)
            mongo_conn.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            mongo_thread = Thread(target=start_mongo)
            mongo_thread.start()
            time.sleep(1)
            mongo_conn = MongoClient(host, port)


def get_collection_count(collection):
    global mongo_conn
    global mongo_db
    while not is_database_unlocked():
        time.sleep(0.003)
    lock_database()
    count = mongo_conn[mongo_db][collection].count()
    unlock_database()
    return count


def get_last_element(collection):
    global mongo_conn
    global mongo_db
    while not is_database_unlocked():
        time.sleep(0.003)
    lock_database()
    count = mongo_conn[mongo_db][collection].count()
    cursor = mongo_conn[mongo_db][collection].find().skip(count-1)
    unlock_database()
    df = pd.DataFrame(list(cursor))
    return df


def is_database_unlocked():
    global mongo_conn
    global mongo_db
    cursor = mongo_conn[mongo_db]["locks"].find()
    cursor_list = list(cursor)
    if len(cursor_list) == 0:
        return True

    lock_type = cursor_list[0]["Type"]
    lock_time = cursor_list[0]['Time']
    time_difference = calendar.timegm(time.gmtime()) - lock_time

    if lock_type == 0 or time_difference > 5:   # 5 seconds is max read/write time
        return True
    return False


def lock_database():
    global mongo_conn
    global mongo_db
    mongo_conn[mongo_db]["locks"].update_one({}, {'$set': {'Type': 1, 'Time': calendar.timegm(time.gmtime())}}, upsert=True)


def unlock_database():
    global mongo_conn
    global mongo_db
    mongo_conn[mongo_db]["locks"].update({}, {'$set': {'Type': 0}})


def read_collection_as_list_mongo(collection, query={}, skip=0, limit=0):
    """ Returns mongo collection as list """
    global mongo_conn
    global mongo_db

    while not is_database_unlocked():
        time.sleep(0.003)
    lock_database()
    if not limit == 0:
        col_list = list(mongo_conn[mongo_db][collection].find(query).skip(skip).limit(limit))
    else:
        col_list = list(mongo_conn[mongo_db][collection].find(query).skip(skip))
    unlock_database()
    return col_list


def collection_update_with_push(collection, query, values):
    global mongo_conn
    global mongo_db
    while not is_database_unlocked():
        time.sleep(0.003)
    lock_database()
    mongo_conn[mongo_db][collection].update_one(query, {"$push": values})
    unlock_database()


def collection_update_with_set(collection, query, value):
    global mongo_conn
    global mongo_db
    while not is_database_unlocked():
        time.sleep(0.003)
    lock_database()
    mongo_conn[mongo_db][collection].update_one(query, {"$set": value}, upsert=True)
    unlock_database()


def collection_update_multiple_with_set(collection, queries, values):
    """ Update multiple documents in same collection.
        Note that length of values and queries need to match!"""
    global mongo_conn
    global mongo_db

    if len(queries) != len(values):
        return

    while not is_database_unlocked():
        time.sleep(0.003)
    lock_database()
    for i, value in enumerate(values):
        mongo_conn[mongo_db][collection].update_one(queries[i], {"$set": value}, upsert=True)
    unlock_database()


# def read_mongo_collection_df_(dictionary, collection, skip, query={}):
#     """ If successful, return dataframe's length, otherwise returns negative number """
#     df = pd.DataFrame(list(mongo_conn[mongo_db][collection].find(query).skip(skip)))
#     if len(df) != 0:
#         df = df.drop(columns="_id")
#         dictionary[collection] = df.drop(columns="CheckSum")
#     return 0


def read_mongo_guaranteed(dictionary, collection, skip=0, query={}):
    """ If successful, return dataframe's length, otherwise returns negative number """
    count_start = -1
    count_end = 0
    df = 0
    while count_end != count_start:
        count_start = mongo_conn[mongo_db][collection].count()
        df = pd.DataFrame(list(mongo_conn[mongo_db][collection].find(query).skip(skip)))
        count_end = mongo_conn[mongo_db][collection].count()
    if len(df) != 0:
        dictionary[collection] = df.drop(columns="_id")
        return len(df)
    return 0


def read_mongo_best_effort(dictionary, collection, skip, query={}):
    """ If successful, return dataframe's length, otherwise returns negative number """
    count_start = mongo_conn[mongo_db][collection].count()
    df = pd.DataFrame(list(mongo_conn[mongo_db][collection].find(query).skip(skip)))
    if count_start != mongo_conn[mongo_db][collection].count():
        return -1   # happens when possible dirty read
    if len(df) != 0:
        dictionary[collection] = df.drop(columns="_id")
        return len(df)
    return 0


# def read_mongo_collection_df_safe(dictionary, collection, skip, query={}):
#     """ If successful, return dataframe's length, otherwise returns negative number """
#     df = pd.DataFrame(list(mongo_conn[mongo_db][collection].find(query).skip(skip)))
#     if len(df) != 0:
#         if df["CheckSum"].iloc[-1] > 0:
#             if len(df) == (df["CheckSum"].iloc[-1]-skip):
#                 df = df.drop(columns="_id")
#                 dictionary[collection] = df.drop(columns="CheckSum")
#                 return len(df)
#             return -1   # Only happens when inner elements are incorrect
#         else:
#             return -1   # Only happens last elements are incorrect
#     return 0

#
# def read_multiple_mongo_collections_df(collections, skips, query={}):
#     """ Reads multiple collections from mongo database.
#         Supports only skip and query options. Query same for all reads.
#         Collections and skips must match in length!"""
#     global mongo_conn
#     global mongo_db
#   #  while not is_database_unlocked():
#    #     time.sleep(0.003)
#   #  lock_database()
#     dict_data_frames = dict()
#    # for i in range(0, len(collections)):
#       #  read_mongo_collection_df(dict_data_frames, collections[i], skips[i])
#
#
#        # df = pd.DataFrame(list(mongo_conn[mongo_db][collections[i]].find(query).skip(skips[i])))
#       #  if len(df) != 0:
#        #     dict_data_frames[collections[i]] = df.drop(columns="_id")
#        # else:
#         #    dict_data_frames[collections[i]] = df
#    # unlock_database()
#     return dict_data_frames

#
# def collection_read_mongo(collection, query={}, no_id=True, skip=0, limit=0):
#     global mongo_conn
#     global mongo_db
#     while not is_database_unlocked():
#         time.sleep(0.003)
#     lock_database()
#     cursor = mongo_conn[mongo_db][collection].find(query).skip(skip).limit(limit)
#     #array = list(mongo_conn[mongo_db][collection].find(query).skip(skip).limit(limit))
#     unlock_database()
#     # TODO: We have to first check the size
#     df = pd.DataFrame(list(cursor))
#
#    # x = []
#    # for i in array:
#     #    x.append(i)
#
#     if no_id:
#         try:
#             del df["_id"]
#         except:
#            pass
#     return df


def insert_document(collection, data):
    global mongo_conn
    global mongo_db
    while not is_database_unlocked():
        time.sleep(0.003)
    lock_database()
    mongo_conn[mongo_db][collection].insert_one(data)
    unlock_database()
