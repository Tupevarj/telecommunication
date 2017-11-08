from django.db import models
from mongoengine import *
import numpy as np
import pandas as pd
from pymongo import MongoClient

# Create your models here.

# from mongoengine import connect
# connect('5gopt', username='yi', password='abc123')

# connect(db='5gopt')

class normal(Document):

    Time = StringField()
    UeNodeNo = StringField()
    UeRNTI = StringField()
    Cell_ID = StringField()
    RSRP = StringField()
    RSRQ = StringField()
    Serving_Cell = StringField()

    meta = {"collection": "normal"}


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





def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)


    return conn[db]


def read_mongo(db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        del df['_id']

    return df

normalDF = read_mongo("5gopt", "normal", no_id=True)
print(normalDF[:5])










