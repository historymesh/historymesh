from django.conf import settings
from restpose import Server

collection = (
    Server(settings.RESTPOSE_CONFIG['uri'])
    .collection(settings.RESTPOSE_CONFIG['collection'])
)

def set_schema():
    collection.checkpoint().wait() # Causes collection to be created as sideeffect.
    config = collection.config
    config['default_type'] = {
        'patterns': [],
        'fields': {
            'id': {'store_field': 'id', 'type': 'id'},
            'type': {'store_field': 'type', 'group': '!', 'type': 'exact'},
            '_meta': {'slot': 0, 'type': 'meta', 'group': '#'},
            'name': {'type': 'text', 'group': 'n', 'processor': 'stem_en', 'store_field': 'name'},
            'text': {'type': 'text', 'group': 't', 'processor': 'stem_en', 'store_field': 'text'},
            'timeline_date': {'type': 'double', 'slot': 'timeline_date', 'store_field': 'timeline_date'},
            'display_date': {'type': 'text', 'group': 'd', 'processor': 'stem_en', 'store_field': 'display_date'}
        }
    }
    collection.config = config

def index(obj):
    doc = obj.search_data()
    collection.doc_type(obj._meta.object_name).add_doc(doc, doc_id=obj.pk)

def build_query(querystr):
    q = (
        collection.field.name.text(querystr) * 5 |
        collection.field.text.text(querystr) * 1.5 |
        collection.field.display_date.text(querystr) * 0.5
    )
    print repr(querystr), q._build_search()

    return q
