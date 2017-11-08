from django.db import models
from mongoengine import *
import numpy as np
import pandas as pd

# Create your models here.

# from mongoengine import connect
# connect('5gopt', username='yi', password='abc123')

connect(db='5gopt')

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
print("Time", normal.objects[0].Time)
print("UeNodeNo", normal.objects[0].UeNodeNo)
print("UeRNTI", normal.objects[0].UeRNTI)
print("cell id", normal.objects[0].Cell_ID)
print("RSRP", normal.objects[0].RSRP)
print("RSRQ", normal.objects[0].RSRQ)
print("Serving_Cell", normal.objects[0].Serving_Cell)
    # print(preProcess())

    # def preProcess():
    #     normalData = pd.DataFrame()
normalData = preProcess()
print(normalData[:5])









