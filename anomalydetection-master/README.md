# anomalydetection
Anomaly Detection based on k Nearest Neighbours. 

Two approaches are implemented. The first is straightforward application of k Nearest Neighbour. Specifically, the distance of each point with respect to all the other points is checked, and the k nearest neighbours are considered to evaluate whether the point is anomalous or not. The latter is performed (straightforwardly) consider if the mean of KNN distances is lower or higher than a user specified value d (which is related to normalized space!). The second approach splits the input data in several samples, and classifies the point as normal immediately when the kNN distance for that point is lower than d. 

Usage of code is specified by "python anomalydetection.py --help" 

Several extensions to the code are of course possible such as Local Outlier Factor (LOF). Also, I am curious to see if a speed-up can be gained if using the pandas library, but that is for another time. 
