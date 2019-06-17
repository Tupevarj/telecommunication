import matplotlib.pyplot as plt
from auxFunctions.osFunctions import fileHandling

# ---------------------------------------------------------------------
def plotInputData():
    """
    Small function to scatterplot the input data.

    :return: scatter plot of 2D inputData
    """
    # 0. Make an instance of the filehandling object
    fileIn = fileHandling()

    # 1. Scatter plot the 2D input data
    plt.scatter(fileIn.inputData[:, 0], fileIn.inputData[:, 1])
    plt.show()

# ---------------------------------------------------------------------
def plotOutputKNN(points, sccolors):
    plt.figure(1)
    plt.scatter(points[:, 0], points[:, 1], c=sccolors)
    plt.title("Scatterplot data. Red points are anomalous.")
    plt.show()