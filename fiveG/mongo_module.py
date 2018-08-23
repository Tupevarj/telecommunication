import sys
import pymongo
from pymongo import MongoClient
from threading import Thread
import subprocess
import time
import pandas as pd


""" 
    data_frames["main_kpis_log"] = data_frames["main_kpis_log"][np.isfinite(data_frames["main_kpis_log"]['RSRP'])] !!!!!
    
    
        update_rem_map_chart(data_frames["rem_log"].tail(22500), context)          # TODO
"""


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

    def read_guaranteed(self, dictionary, collection, skip=0, query={}):
        """ If successful, return dataframe's length, otherwise returns negative number """
        count_start = -1
        count_end = 0
        df = 0
        while count_end != count_start:
            count_start = self.client[self.db_name][collection].count()
            df = pd.DataFrame(list(self.client[self.db_name][collection].find(query).skip(skip)))
            count_end = self.client[self.db_name][collection].count()
        if len(df) != 0:
            dictionary[collection] = df.drop(columns="_id")
            return len(df)
        return 0

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


class CollectionReader:
    #is_updated = False  # Probably not needed!
    data = dict()
    name = ''
    last_read = 0

    def __init__(self, name):   # Maybe add skippable property
        self.name = name

    def reset(self):
        self.last_read = 0

   # def update(self, mongo_connector):
   #     data = mongo_connector.read_guaranteed(dictionary=self.data, collection=self.name, skip=self.last_read)
        #temp = self.last_read
   #     self.last_read = len(data)
        #if self.last_read == temp:
         #   self.is_updated = True
        #else:
         #   self.is_updated = False

    def get_data(self):
        return self.data


class MongoModule:
    """ Buffer. This should control reading information amount. """
 #   mongo_collections = list()
    mongo_connector = MongoDbConnector()
   # time_since_update = sys.maxsize

   # def __init__(self):
    #    """ Here is a list of all the collection in DB. """
    #    self.add_mongo_collection('throughput_log')
   #     self.add_mongo_collection('main_kpis_log')
    #    self.add_mongo_collection('status_log')
    #    self.add_mongo_collection('event_log')
    #    self.add_mongo_collection('rem_log')        # TAIL?

  #  def add_mongo_collection(self, name):
  #      self.mongo_collections.append(CollectionReader(name))

    def update_reader(self, collection_reader):
        self.mongo_connector.read_guaranteed(dictionary=collection_reader.data, collection=collection_reader.name, skip=collection_reader.last_read)
        collection_reader.last_read = len(collection_reader.data)
        return collection_reader.data
       # collection_reader.update(self.mongo_connector)


    #def update(self):
     #   for collection in self.mongo_collections:
       #     collection.update(self.mongo_connector)

    #def get_collections(self):
    #    data = dict()
    #    for collection in self.mongo_collections:
    #        data[collection.name] = collection.get_data()
   #     return data
