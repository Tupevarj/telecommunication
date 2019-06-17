#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from anomalyKNN.kNN import kNNstraightforward, kNNsampled
from auxFunctions.plotFunctions import plotInputData, plotOutputKNN
import time
from auxFunctions.osFunctions import writeOutputKNN

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="anomaly detection based on k Nearest Neighbour (kNN)")
    parser.add_argument("-t", "--train", help="apply kNN on the training set (default false). "
                                        "This argument needs to be set to perform the KNN "
                                        "anomaly detection.", action="store_true", default=False)
    parser.add_argument("-k", type=int, help="chose the value of k (default 1)", default=1)
    parser.add_argument("-d", type=float, help="chose the value of d (threshold - distance) (default 0.1). "
                                               "Please note this is in normalized space", default=0.1)
    parser.add_argument("--plot", help="plot the training data", action="store_true", default=False)

    args = parser.parse_args()

    if args.plot:
        print(" !====================================================")
        print(" ! Plotting the training data ")
        print(" !====================================================")

        plotInputData()

    if args.train:
        print(" !====================================================")
        print(" ! Applying kNN anomaly to entire training set ")
        print(" !====================================================")

        # 1.0 Straightforward application of kNN
        print(" ! 1. Straightforward application of kNN: ")
        print(" !====================================================")
        start_time = time.time()
        inputD, scoreC,  anomalyList = kNNstraightforward(args.k, args.d)

        # 1.2 Present results
        writeOutputKNN(start_time, anomalyList, 'Straightforward')
        plotOutputKNN(inputD, scoreC)

        #-----------------------------------------------------------------------------

        # 2.0 Applying kNN in samples to save computation time
        print(" !====================================================")
        print(" ! 2. Sampled application of kNN: ")
        print(" !====================================================")
        start_time = time.time()
        inputD, scoreC, anomalyList = kNNsampled(args.k, args.d)

        # 2.1 Present results
        writeOutputKNN(start_time, anomalyList, 'Sampled')
        plotOutputKNN(inputD, scoreC)

        # -----------------------------------------------------------------------------

        # 3.0 Applying kNN in samples using pandas frame work to save computation time
        print(" !====================================================")
        print(" ! 3. Sampled application of kNN using pandas: ")
        print(" !    => another time ... ")
        print(" !====================================================")


    else:
        print(" !====================================================")
        print(" ! Doing nothing ")
        print(" ! ---------------")
        print(" ! ")
        print(" ! Please check 'python anomalydetection --help' on use of code ")
        print(" !====================================================")

