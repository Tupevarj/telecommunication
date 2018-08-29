
from .data_processing import preprocess_training_set_to_8_and_10_dimensions,\
    preprocess_testing_set_to_10_dimensions, preprocess_cod_train, preprocess_cod
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
from .mongo_connector import CollectionReader
from .base_classes import ModuleBase
import sys
import math
from scipy import stats
from scipy.spatial import distance
import json

"""

cod_module.py contains COD classifier and COD module classes.

- Tuukka Varjus < tupevarj@student.jyu.fi >

"""


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

    @staticmethod
    def calculate_z_scores(predictions, locations_ue, locations_bs):
        """ Calculates Z-scores based: based on anomaly users per basestation. """
        ue_per_basestation = np.tile(0, len(locations_bs))
        indicies = np.nonzero(predictions > 0.25)               # Indicies of anomaly users (prediction bigger than 0.25 (threshold)).
        for index in indicies:
            sq_distances = np.empty(0)
            for bs in locations_bs:                             # Find nearest basestation.
                sq_distances = np.append(sq_distances, ((bs[0] - locations_ue[index[0]][0]) ** 2) + ((bs[1] - locations_ue[index[0]][1]) ** 2))
            ue_per_basestation[np.argmin(sq_distances)] += 1    # Add user to nearest basestation

        # Calculate Z-scores
        return list(stats.zscore(ue_per_basestation))

    def validate(self, data, labels, locations_ue, locations_bs):
        """ Validates the model. Stores ROC curve points and AUC score. """     # 8 dimensional data.
        predictions = cross_val_predict(self.model, data, labels, cv=6)
        false_positive_rate, true_positive_rate, thresholds = roc_curve(labels, predictions)

        self.roc_points = list(zip(false_positive_rate, true_positive_rate))
        self.auc_score = auc(false_positive_rate, true_positive_rate)

        # Calculate reference Z-scores:
        predictions = self.model.predict(data)
        self.reference_scores = self.calculate_z_scores(predictions=predictions, locations_ue=locations_ue, locations_bs=locations_bs)

    def save(self):
        """ Saves classifier to hard-drive. Needs to be validated before saving. """

        if not self.roc_points:
            print('CodClassifier error while saving: please train and validate model before saving.')
            return -1
        # save model to pkl file:
        #joblib.dump(self.model, self.name + '.pkl')
        # save ROC curve data to csv file:
        write_to_csv_file(file_name=self.name + '_curve', column_names=['X', 'Y'], data=self.roc_points)
        # save auc score:
        write_to_csv_file(file_name=self.name + '_auc', column_names=['AUC'], data=self.auc_score)
        # save reference z scores:
        write_to_csv_file(file_name=self.name + '_ref_z', column_names=['Ref'], data=self.auc_score)

    def load(self):
        """ Load classifier from hard-drive. """

        # TODO: confirm that exists. RETURN 0 IN THAT CASE!
        # load model from pkl file:
        self.model = joblib.load(self.name + '.pkl')

        # load ROC curve data from csv file:
        roc = pd.read_csv(self.name + '_curve.csv')
        self.roc_points = (np.array(roc)).tolist()
        # load auc score from csv file
        roc = pd.read_csv(self.name + '_auc.csv')
        self.auc_score = (np.array(roc)).tolist()[0]
        # TODO: read reference Z-scores!

    def create(self):
        """ TODO: IMPLEMENT THIS! """
        self.reference_scores = [1, 2, 4, 0, 2, 5, 4]
        self.roc_points = [[0, 0], [0, 0], [0, 0]]
        self.auc_score = 0.93


class CodModule(ModuleBase):
    """ Here we change model, COD engine only know active model.
        Can only predict one cell as a broken. """

    cell_locations = list()     # Location of all cells in scenario.    TODO: Make numpy!
    models = dict()             # Dictionary of classifiers.
    active_model = ''           # Name of active classifier.

    # Consecutive predictions

    def __init__(self, mongo_connector):
        ModuleBase.__init__(self, mongo_connector=mongo_connector)
        """ Here is a list of all the collection in DB and regression models needed in COD module. """
        self.add_mongo_collection_reader('main_kpis_log')
        self.add_mongo_collection_reader('main_kpis_log')
        self.add_mongo_collection_reader('cell_configurations')
        """ Here we add all the classifiers used in cell outage detection. """
        self.add_classifier('linear', LinearRegression())
        self.add_classifier('decision_tree', DecisionTreeRegressor(random_state=0))
        self.add_classifier('random_forest', RandomForestRegressor(n_estimators=10, random_state=0))
        self.add_classifier('svr', SVR(kernel='rbf'))
        self.active_model = 'linear'
        # WE NEED NUMBER OF CELLS AND THEIR LOCATIONS!!

    def add_classifier(self, name, model):
        """ Adds new classifier. """
        self.models[name] = CodClassifier(model=model, name=name)

    def initialize(self):
        """ Initialize Z-score chart. TODO: Remove this! """
        z_scores_chart = dict()
        z_scores = dict()
        z_scores_chart['BS'] = ["BS1", "BS2", "BS3", "BS4", "BS5", "BS6", "BS7"]
        z_scores_chart['Ref. Z-scores'] = [0, 0, 0, 0, 0, 0, 0]
        z_scores_chart['Z Score'] = [0, 0, 0, 0, 0, 0, 0]
        z_scores['ZScores'] = z_scores_chart
        return z_scores

    def __create_models(self):
        """ Loads all classifiers from hard-drive. TODO: UPDATE NB CELLS HERE!"""

        response = dict()

        if len(self.cell_locations) == 0:
            if self.__intialize_cell_locations() != 0:
                print("error in COD module: no cell information found.")
                return response

        # Pre-process data:
        self._mongo_collection_readers[1].reset()
        data_frame = self._mongo_connector.update_reader(self._mongo_collection_readers[1])
        processed = preprocess_cod_train(data_frame=data_frame)
        data_train, data_test, labels_train, labels_test = train_test_split(processed['data'], processed['labels'], test_size=0.2, random_state=7)

       # for key, value in self.models.items():
       #     value.create()
        for key, classifier in self.models.items():
            classifier.train(data=data_train[:, 2:], labels=labels_train)
            classifier.validate(data=data_test[:, 2:], labels=labels_test, locations_ue=data_test[:, :2], locations_bs=self.cell_locations)
            response[classifier.name] = classifier.roc_points
            response[classifier.name + "AUC"] = json.dumps(classifier.auc_score)

        response['ZScores'] = dict()
        response['ZScores']['BS'] = ["BS1", "BS2", "BS3", "BS4", "BS5", "BS6", "BS7"]        # TODO: number of cells!
        response['ZScores']['Ref. Z-scores'] = self.models[self.active_model].reference_scores
        return response

    def __save_models(self):
        """ Saves all classifiers to hard-drive. """
        for key, value in self.models.items():
            value.save()
        return 1

    def __load_models(self):
        response = dict()
        for key, value in self.models.items():
            value.load()
            response[value.name] = value.roc_points
            response[value.name + "AUC"] = value.auc_score

        response['ZScores'] = self.models[self.active_model].reference_scores

        return 1

    def __create(self):

        data_frame = self._mongo_connector.update_reader(self._mongo_collection_readers[0])

        data = np.empty(0)
        labels = np.empty()
        preprocess_cod_train(data=data, labels=labels, data_frame=data_frame)

        # FOR PREDICTION RSRP, RSRQ are needed... 8 dimensional plus locations plus labels
        # Pre process to less dimensions, get locations...

        #self._mongo_connector       # TODO: Call this from update!
        # With preprocessing get data and labels

        data_train, data_test, labels_train, labels_test = train_test_split(data, labels, test_size=0.2, random_state=7)

        for classifier in self.models:
            classifier.train(data=data_train[:, 2:], labels=labels_train)
            classifier.validate(data=data_test[:, 2:], labels=labels_test, locations_ue=data_test[:, :2], locations_bs=self.cell_locations)

    def __change_model(self, params):
        """ Changes model. SHOULD ADD TRY STATEMENT HERE! """
        self.active_model = params["selectedReg"]
        return {'ZScores': self.models[self.active_model].reference_scores}

    def __intialize_cell_locations(self):
        self._mongo_collection_readers[2].reset()
        self.cell_locations = list()
        data_frame = self._mongo_connector.update_reader(self._mongo_collection_readers[2])
        if len(data_frame) == 0:
            return -1
        for index, row in data_frame.iterrows():
            self.cell_locations.append([row['LocationX'], row['LocationY']])
        return 0

    def __run_ml(self):

        if not self.cell_locations:
            #self.intialize_cell_locations()        # TODO: implement this!
            if not self.cell_locations:
                print("error in COD module: no cell information found.")
                return dict() # return -1
        return dict()
        collections = dict()
        for collection in self._mongo_collection_readers:
            collections[collection.name] = self._mongo_connector.update_reader(collection)

        preprocess_cod(collections['main_kpis_log'])
        # PREPROCESS
        self.models[self.active_model].predict()
        self.cod_engine.predict()
        # Pre process module?

        preprocess_cod_train # TODO: use this here!
       # array_10_dim = preprocess_testing_set_to_10_dimensions(collections["main_kpis_log"])
       # ml_data = run_ml(array_10_dim)  # ML data has outage cell ID in first element and Z-scores in second element

        # Z-SCORES

    def execute_command(self, command, params):
        """ Override of ModuleBase interface method. Execute commands
            based on path request <command> string. CHECK urls.py!

            Needs instance of Mongo module to get data needed for
            executing commands. """

        response_data = 0
        if command == '/update_alarm_gui':
            response_data = self.__run_ml()
        elif command == '/createModels':
            response_data = self.__create_models()
        elif command == '/saveMLModels':
            response_data = self.__save_models()
        elif command == '/loadMLModels':
            response_data = self.__load_models()
        elif command == '/selectRegressionModel':
            response_data = self.__change_model(params)
        return response_data
