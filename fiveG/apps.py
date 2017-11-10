from django.apps import AppConfig
from django.db.models import normalCol_read_mongo

class FivegConfig(AppConfig):
    name = 'fiveG'


#     get "normal" collection data from model layer
    def getNormalColData(self):
        normalCol = normalCol_read_mongo("5gopt", "normal", no_id=True)
        return normalCol




