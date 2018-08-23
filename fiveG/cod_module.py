
from .data_processing import preprocess_training_set_to_8_and_10_dimensions,\
    preprocess_testing_set_to_10_dimensions
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.externals import joblib
from .system_output import write_to_csv_file
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
from .mongo_module import CollectionReader
import sys
import math
from scipy import stats
from scipy.spatial import distance

class CodClassifier:
    """ Single classifier for COD. """
    reference_scores = []
    roc_points = list()
    auc_score = 0
    model = 0
    name = ''

    def __init__(self, model, name):
        self.model = model
        self.name = name

    def train(self, data, labels):
        """ Trains model. """
        self.model.fit(data, labels)

    def calculate_z_scores(self, predictions, locations_ue, locations_bs):
        """ Calculates Z-scores based: based on anomaly users per basestation. """
        ue_per_basestation = np.tile(0, len(locations_bs))
        indicies = np.nonzero(predictions > 0.25)               # Indicies of anomaly users (prediction bigger than 0.25 (threshold)).
        for index in indicies:
            sq_distances = np.empty(0)
            for bs in locations_bs:                             # Find nearest basestation.
                sq_distances = np.append(sq_distances, ((bs[0] - locations_ue[index][0]) ** 2) + ((bs[1] - locations_ue[index][1]) ** 2))
            ue_per_basestation[np.argmin(sq_distances)] += 1    # Add user to nearest basestation

        # Calculate Z-scores
        return stats.zscore(ue_per_basestation)


    def validate(self, data, labels, locations_bs):
        """ Validates the model. Stores ROC curve points and AUC score. """     # 8 dimensional data.
        predictions = cross_val_predict(self.model, data, labels, cv=6)
        false_positive_rate, true_positive_rate, thresholds = roc_curve(labels, predictions)

        self.roc_points = list(zip(false_positive_rate, true_positive_rate))
        self.auc_score = auc(false_positive_rate, true_positive_rate)

        # Calculate reference Z-scores:    TODO: Only location needed!
        predictions = self.model.predict(np.asarray(data)[:, 4:])
        reference_scores = self.calculate_z_scores(predictions=predictions, locations_ue=data["LocationX"], locations_bs=locations_bs)

#    def predict(self, data):
 #       # Preprocess here.


    #def change_model(self, model):
     #   self.active_model = model

    def save(self):
        """ Saves classifier to hard-drive. Needs to be validated before saving. """

        if not self.roc_points:
            print('CodClassifier error while saving: please train and validate model before saving.')
            return -1
        # save model to pkl file:
        joblib.dump(self.model, self.name + '.pkl')
        # save ROC curve data to csv file:
        write_to_csv_file(file_name=self.name + '_curve', column_names=['X', 'Y'], data=self.roc_points)
        # save auc score:
        write_to_csv_file(file_name=self.name + '_auc', column_names=['AUC'], data=self.auc_score)
        # save reference z scores:
        write_to_csv_file(file_name=self.name + '_ref_z', column_names=['Ref'], data=self.auc_score)

    def load(self):
        """ Load classifier from hard-drive. """

        # TODO: confirm that exists.
        # load model from pkl file:
        self.model = joblib.load(self.name + '.pkl')

        # load ROC curve data from csv file:
        roc = pd.read_csv(self.name + '_curve.csv')
        self.roc_points = (np.array(roc)).tolist()
        # load auc score from csv file

        # TODO: read reference Z-scores!


class CodModule:
    """ Here we change model, COD engine only know active model.
        Can only predict one cell as a broken. """

    mongo_collections = list()  # Collections in MongoDB needed in COD Module.
    cell_locations = list()     # Location of all cells in scenario.
    mongo_module = 0            # 'Pointer' to Mongo Module to extract data.
    models = dict()             # Dictionary of classifiers.
    active_model = ''           # Name of active classifier.

    # Consecutive predictions

    def __init__(self, mongo_module):
        """ Here is a list of all the collection in DB and regression models needed in COD module. """
        self.add_mongo_collection('main_kpis_log')
        self.add_classifier('linear', LinearRegression())
        self.add_classifier('decision_tree', DecisionTreeRegressor(random_state=0))
        self.add_classifier('random_forest', RandomForestRegressor(n_estimators=10, random_state=0))
        self.add_classifier('svr', SVR(kernel='rbf'))
        # WE NEED NUMBER OF CELLS AND THEIR LOCATIONS!!
        self.mongo_module = mongo_module

    def add_mongo_collection(self, name):
        self.mongo_collections.append(CollectionReader(name))

    def add_classifier(self, name, model):
        """ Adds new classifier. """
        self.models[name] = CodClassifier(model=model, name=name)

    def train_and_validate(self):
        self.mongo_module       # TODO: Call this from update!
        # With preprocessing get data and labels

    def update(self):

        if not self.cell_locations:
            self.intialize_cell_locations()
            if not self.cell_locations:
                print("error in COD module: no cell information found.")
                return -1

        collections = dict()
        for collection in self.mongo_collections:
            collections[collection.name] = self.mongo_module.update_reader(collection)

        self.cod_engine.predict()
        # Pre process module?
        array_10_dim = preprocess_testing_set_to_10_dimensions(collections["main_kpis_log"])
       # ml_data = run_ml(array_10_dim)  # ML data has outage cell ID in first element and Z-scores in second element

        # Z-SCORES
