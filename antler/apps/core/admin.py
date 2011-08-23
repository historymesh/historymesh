from django.contrib import admin
from core.models import Edge, Person, Concept, Object, Event

admin.site.register(
    Edge,
    list_display=[
        'id',
        'subject_type',
        'subject_id',
        'object_type',
        'object_id',
        'verb',
    ],
    list_filter = [
        'subject_type',
        'object_type',
        'verb',
    ],
)

admin.site.register(Person)
admin.site.register(Concept)
admin.site.register(Object)
admin.site.register(Event)

