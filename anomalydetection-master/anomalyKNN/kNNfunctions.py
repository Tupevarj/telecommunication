import numpy as np
from auxFunctions.osFunctions import fileHandling

class kNN(fileHandling):
    '''

    '''
    def __init__(self):
        """

        :rtype: object
        """
        super(kNN,self).__init__()


    def normalizeAndTransInput2D(self, data2handle):
        """
        Normalize and translate 2D input such that max. distance in x- and y- direction
        both equal 1 and left bottom corner starts at (x,y) = (0,0).
        :param: data to normalize
        """

        dd = np.array(data2handle)
        self.xMax = np.absolute(np.max(data2handle[:, 0])) + np.absolute(np.min(data2handle[:, 0]))
        dd[:, 0] = data2handle[:, 0] / self.xMax

        self.yMax = np.absolute(np.max(data2handle[:, 1])) + np.absolute(np.min(data2handle[:, 1]))
        dd[:, 1] = data2handle[:, 1] / self.yMax

        cor = [np.absolute(np.min(dd[:, 0])), np.absolute(np.min(dd[:, 1]))]
        self.cor = np.array(cor)

        self.inputNormT = dd + self.cor
        del dd

    def distanceEuclidean2D(self, p1, p2):
        """
        Compute the Euclidean distance between 2 points.
        :param p1: point one (x, y)
        :param p2: point two (x,y)
        :return: Euclidean distance between 2 points
        """
        #
        # TODO: check if this function should be in the object or out.
        #
        dist = np.sqrt(np.power(np.absolute(p1[0] - p2[0]), 2.) +
                       np.power(np.absolute(p1[1] - p2[1]), 2.) )
        return dist


    def transformPointBack2D(self, pcoord):
        """
        Transform point back to the 'original' space:
        1- translate
        2- multiply with normalizer
        :param: pcoord: point to be transformed
        :return: tpoint: transformed point
        """

        tpoint = pcoord - self.cor
        tpoint[0] = tpoint[0] * self.xMax
        tpoint[1] = tpoint[1] * self.yMax
        return tpoint


    def divide2samples(self, numSamples):
        """
        Devide the input data into numSamples of different samples. The
        :param numSamples: amount of requested different samples
        :return: inputDataSamples
        """
        inputRand = self.inputNormT
        np.random.shuffle(inputRand)
        self.inputDataSamples = np.array_split(inputRand, numSamples)
        self.inputDataSamples = np.array(self.inputDataSamples)


    def distanceKNN(self, pCheck, pTrain, k):
        """
        Find the distance to the k Nearest Neighbours.
        Method utilizes:
         -/ distanceEuclidean2D.
        :param pCheck: point to check
        :param pTrain: dataset to compare with
        :param k: number of nearest neighbours
        :return: distKNN: array with distances to the k Nearest Neighbours
        """
        dList = []
        for p in pTrain:
            dList.append(self.distanceEuclidean2D(pCheck, p))
        dList = np.array(dList)
        dList = np.sort(dList)
        if (dList[0] == 0):
            distKNN = dList[1:k+1]
        else:
            distKNN = dList[:k]
        del dList
        return distKNN

