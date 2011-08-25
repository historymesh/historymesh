
from django.conf import settings

try:
    from restpose import Server
except ImportError:
    # Allow the site to work without search
    class Server(object):
        fake = True
        def __init__(self, *args, **kwargs):
            pass

server = Server(settings.RESTPOSE_CONFIG['uri'])

def index(obj):
    if hasattr(server, 'fake'):
        raise RuntimeError("restpose client not installed")
    print obj
