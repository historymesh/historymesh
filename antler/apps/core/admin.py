from django.contrib import admin
from core.models import Edge, Person, Concept, Object, Event

admin.site.register(
    Edge,
    list_display=[
        'id',
        'subject',
        'object',
        'verb',
    ],
    list_filter = [
        'subject_type',
        'object_type',
        'verb',
    ],
)

class NodeAdmin(admin.ModelAdmin):
    list_display = ["name", "timeline_date", "display_date"]
    list_editable = ["timeline_date", "display_date"]

admin.site.register(Person, NodeAdmin)
admin.site.register(Concept, NodeAdmin)
admin.site.register(Object, NodeAdmin)
admin.site.register(Event, NodeAdmin)

