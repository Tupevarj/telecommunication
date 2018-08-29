import pymongo
from pymongo import MongoClient
from threading import Thread
import subprocess
import time
import pandas as pd


class Singleton(object):
    """ Singleton base class. """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class MongoDbConnector:
    """ MongoDB connector class. Handles all the operations with MongoDB. """

    client = MongoClient()
    db_name = "5gopt"

    @staticmethod
    def start_server():
        subprocess.call(["./start_mongo.sh"])

    def connect(self):
        """ A util for making a connection to mongo """
        host = "localhost"
        port = 27017
        username = ""
        password = ""

        if username and password:
            mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, self.db_name)
            self.client = MongoClient(mongo_uri)
        else:
            try:
                self.client = MongoClient(host, port, serverSelectionTimeoutMS=2)
                self.client.server_info()
            except pymongo.errors.ServerSelectionTimeoutError:
                mongo_thread = Thread(target=self.start_mongo)
                mongo_thread.start()
                time.sleep(1)
                self.client = MongoClient(host, port)

    def read_guaranteed(self, collection, skip=0, query={}):
        """ If successful, return dataframe's length, otherwise returns negative number """
        count_start = -1
        count_end = 0
        df = 0
        while count_end != count_start:
            count_start = self.client[self.db_name][collection].count()
            df = pd.DataFrame(list(self.client[self.db_name][collection].find(query).skip(skip)))
            count_end = self.client[self.db_name][collection].count()
        if len(df) != 0:
            #  df = df[np.isfinite(df)]   # Remove infinity numbers if needed!
            df = df.drop(columns="_id")
        return df

    def read(self, dictionary, collection, skip, query={}):
        """ If successful, return dataframe's length, otherwise returns negative number """
        count_start = self.client[self.db_name][collection].count()
        df = pd.DataFrame(list(self.client[self.db_name][collection].find(query).skip(skip)))
        if count_start != self.client[self.db_name][collection].count():
            return -1  # happens when possible dirty read
        if len(df) != 0:
            dictionary[collection] = df.drop(columns="_id")
            return len(df)
        return 0

    def update_multiple_by_set(self, collection, queries, values):
        """ Update multiple documents in same collection.
            Note that length of values and queries need to match!"""
        if len(queries) != len(values):
            return
        for i, value in enumerate(values):
            self.client[self.db_name][collection].update_one(queries[i], {"$set": value}, upsert=True)

    def get_collection_count(self, collection):
        return self.client[self.db_name][collection].count()


class CollectionReader:
    """ Collection reader is container class updatable through MongoConnector class.
        Is tied to one collection in database and keeps count of read elements. """
    data = dict()
    name = ''
    last_read = 0
    primary = False

    def __init__(self, name, primary=False):
        self.name = name
        self.primary = primary

    def reset(self):
        self.last_read = 0

    def get_data(self):
        return self.data


class CollectionWriter:
    """ Collection writer is container class updatable through MongoConnector class.
        Is tied to one collection in database and requires updating queries and values
        for writing. SHOULD ADD UPDATE METHOD OPTION! CURRENTLY WRITES WITH SET METHOD!
    """
    name = ''
    queries = []
    values = []

    def __init__(self, name, query=[], values=[]):
        self.name = name
        self.queries = query
        self.values = values

    def set_queries(self, query):
        self.queries = query

    def set_values(self, values):
        self.values = values


class MongoConnector(Singleton):
    """ Mongo Connector controls updating collection writers and readers. """

    mongo_connector = MongoDbConnector()

    def update_writer(self, collection_writer):
        """ Updates writer (Writes changes to database, with SET OPTION!) """
        self.mongo_connector.update_multiple_by_set(collection=collection_writer.name, queries=collection_writer.queries, values=collection_writer.values)

    def update_reader(self, collection_reader):
        """ Updates reader (Reads new data from database) """
        collection_reader.data = self.mongo_connector.read_guaranteed(collection=collection_reader.name, skip=collection_reader.last_read)
        collection_reader.last_read += len(collection_reader.data)
        return collection_reader.data

    def check_initialized(self, collection_reader):
        """ Check if database is initialized. Returns true if
            primary collection reader is initialized. """
        if collection_reader.last_read > self.mongo_connector.get_collection_count(collection_reader.name):
            collection_reader.reset()
            if collection_reader.primary:
                return True
        return False
