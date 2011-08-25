
from django.conf import settings
from restpose import Server

server = Server(settings.RESTPOSE_CONFIG['uri'])

def index(obj):
    print obj.search_data
