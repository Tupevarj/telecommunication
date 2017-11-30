from django.db import models
# from mongoengine import *
import numpy as np
import pandas as pd
from pymongo import MongoClient


# from mongoengine import connect
# connect('5gopt', username='yi', password='abc123')

# connect(db='5gopt')
#




def preProcess():
    normalDF = pd.DataFrame(columns=["Time", "UeNodeNo", "UeRNTI", "Cell_ID", "RSRP", "Serving_Cell"])

    index = 0
    for doc in normal.objects[:1000]:
        normalDF.loc[index] = [doc.Time, doc.UeNodeNo, doc.UeRNTI, doc.Cell_ID, doc.RSRP, doc.Serving_Cell]
        index = index + 1
    print("finish load")
    return normalDF
#


# for i in normal.objects[:1]:
# print("Time", normal.objects[0].Time)
# print("UeNodeNo", normal.objects[0].UeNodeNo)
# print("UeRNTI", normal.objects[0].UeRNTI)
# print("cell id", normal.objects[0].Cell_ID)
# print("RSRP", normal.objects[0].RSRP)
# print("RSRQ", normal.objects[0].RSRQ)
# print("Serving_Cell", normal.objects[0].Serving_Cell)
    # print(preProcess())

    # def preProcess():
    #     normalData = pd.DataFrame()
# normalData = preProcess()
# print(normalData[:5])



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


# collection for cell indicator, ns3 can read command from this collection
# class CellIndicator(Document):
#     cell = IntField()
#     flag = IntField()   #0 means False; 1 means True


# build connection between already-existing collection and mongoengine collection
# class EventLog(Document):
#     meta = {'collection': 'event_log'}

# class Control(models.Model):
#     cellID = models.IntegerField()
#     normal = models.IntegerField()
#     outage = models.IntegerField()
#     coc = models.IntegerField()
#     cco = models.IntegerField()
#     mro = models.IntegerField()
#     mlb = models.IntegerField()
def insert_document(collection, data):
    db = _connect_mongo()
    db[collection].insert_one(data)


















