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
    'uri': 'http://10.0.0.52:7777/',
    'collection': 'antler',
}
