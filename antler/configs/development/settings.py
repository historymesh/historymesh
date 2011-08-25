from antler.configs.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '',
        'USER': 'antler',
        'PASSWORD': 'antler',
        'NAME': 'antler',
    }
}

RESTPOSE_CONFIG = {
    'host': '127.0.0.1',
    'port': 7777,
    'collection': 'antler',
}
