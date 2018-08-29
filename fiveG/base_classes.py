from .mongo_connector import CollectionReader, CollectionWriter

""" 

This file contains base classes that are used in backend. 

Base classes (interfaces) in here serve
as guideline understanding the design pattern. 
    
- Tuukka Varjus <tupevarj@student.jyu.fi> 

"""


class ModuleBase:
    """ Interface for module system where module executes
        commands from front-end and reply with response data.

        Mongo collections are collections (tables) in Mongo database
        that module requires to read/write to executing commands. """

  #  _mongo_collection_readers = list()              # List of Mongo collection readers
  #  _mongo_collection_writers = list()              # List of Mongo collection writers. SHOULD BE DICTIONARY!
  #  _mongo_connector = 0                            # 'Pointer' to Mongo Connector to extract data.

    def __init__(self, mongo_connector):
        self._mongo_connector = mongo_connector
        self._mongo_collection_readers = list()
        self._mongo_collection_writers = list()

    def add_mongo_collection_reader(self, name, primary=False):
        self._mongo_collection_readers.append(CollectionReader(name, primary))

    def add_mongo_collection_writer(self, name, queries=[], values=[]):
        self._mongo_collection_writers.append(CollectionWriter(name, queries, values))

    def execute_command(self, command, params):
        pass

    def initialize(self):
        pass

