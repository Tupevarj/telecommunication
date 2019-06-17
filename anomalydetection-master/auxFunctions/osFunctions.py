import csv
import numpy as np
import Tkinter, tkFileDialog
import time
import matplotlib.pyplot as plt
import os

def writeOutputKNN(stime, anomList, stringG):
    print stringG, "kNN has taken %s seconds:" % (time.time() - stime)
    print "The following points are recongnized as anomalies:"
    for p in anomList:
        print "(x, y) equal to:", p[0], p[1]


class fileHandling(object):
    """
    Basic Object Properties for file handling.
    :return: inputData: class variable with the 2D inputdata
    """
    def __init__(self):
        runDir = os.getcwd()
        fn = os.path.join(runDir, '../reduceDims/mds2dims_X_train_1000samples.csv')
        ifile = open(fn, 'rb')

        reader = csv.reader(ifile)
        inData = []
        for row in reader:
            x = float(row[0])
            y = float(row[1])
            rowIn = [x, y]
            inData.append(rowIn)
        self.inputData = np.array(inData)
        del inData # is probably quite overkill ..

