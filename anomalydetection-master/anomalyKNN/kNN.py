from kNNfunctions import kNN
import numpy as np

# -----------------------------------------------------------------------------
def kNNstraightforward(k, d):
    """
    Straighforward application of KNN algorithm to identify the anomalous points.
    :param k: value of k for the k nearest neighbour
    :param d: threshold value for distance to consider a point anomalous (d is specified in normalized space)
    :return: the anomalous points, a score list and the input data
    """

    # 0. initiate instance of kNN classe
    anomKNN = kNN()

    # 1. normalize and translate 2D input data
    anomKNN.normalizeAndTransInput2D(anomKNN.inputData)

    # 2.0 find the averaged distance to the k Nearest Neighbours
    # 2.1 find the anomalies: when averaged distance is larger and d
    # 2.2 make an anomaly score
    # TODO: decide whether loop below should be in kNNfunctions - and clean up accordingly
    sList = []
    anomalyList = []
    for tp in anomKNN.inputNormT:
        dist2neighbours = anomKNN.distanceKNN(tp, anomKNN.inputNormT, k)
        sList.append(np.mean(dist2neighbours))
        if (np.mean(dist2neighbours) > d):

            # transform back to normal space to present results
            tpBack = anomKNN.transformPointBack2D(tp)
            anomalyList.append(tpBack)

    anomalyList = np.array(anomalyList)
    sList = np.array(sList)

    # 3. use the averaged distance as score in a scatter plot
    scorecolors = ['red' if value > d else 'blue' for value in sList]

    return anomKNN.inputData, scorecolors, anomalyList


# -----------------------------------------------------------------------------
def kNNsampled(k, d):
    """
    Straighforward application of KNN algorithm to identify the anomalous points.
    :param k: value of k for the k nearest neighbour
    :param d: threshold value for distance to consider a point anomalous (d is specified in normalized space)
    :return: the anomalous points, a score list and the input data
    """

    # 0. initiate instance of kNN classe
    anomKNN = kNN()

    # 1. normalize and translate 2D input data
    anomKNN.normalizeAndTransInput2D(anomKNN.inputData)

    # 2. divide the data set into different samples of the randomized array
    numSamples = 10
    anomKNN.divide2samples(numSamples)

    # 3.0 find the
    # TODO: decide whether loop below should be in kNNfunctions - and clean up accordingly
    sList = []
    aList = []
    inputDataTrans = []

    for tp in anomKNN.inputNormT:
        dist2closestneighbours = np.array([])
        for i in np.arange(len(anomKNN.inputDataSamples)):

            dist2neighbours = anomKNN.distanceKNN(tp, anomKNN.inputDataSamples[i], k)
            dist2closestneighbours = np.append(dist2closestneighbours,dist2neighbours)
            dist2closestneighbours = np.sort(np.array(dist2closestneighbours))[:k]

            if (np.mean(dist2closestneighbours) < d):
                sList.append(np.mean(dist2closestneighbours))
                break

            if (i == (len(anomKNN.inputDataSamples) - 1) ):
                sList.append(np.mean(dist2closestneighbours))
                tpBack = anomKNN.transformPointBack2D(tp)
                aList.append(tpBack)

        # TODO: for some reason the order of anomKNN.inputNorm differs from anomKNN.inputData; to check
        tpB = anomKNN.transformPointBack2D(tp)
        inputDataTrans.append(tpB)

    aList = np.array(aList)
    sList = np.array(sList)
    inputDataTrans = np.array(inputDataTrans)

    # 3. use the averaged distance as score in a scatter plot
    scorecolors = ['red' if value > d else 'blue' for value in sList]

    return inputDataTrans, scorecolors, aList







