from django.contrib import admin
from core.models import Edge, Person, Concept, Object, Event, StoryContent, ExternalLink, Story

admin.site.register(
    Edge,
    list_display=[
        'id',
        'story',
        'subject',
        'verb',
        'object',
    ],
    list_filter = [
        'subject_type',
        'object_type',
        'verb',
    ],
)

class NodeAdmin(admin.ModelAdmin):
    list_display = ["name", "timeline_date", "display_date", "reference_url"]
    list_editable = ["timeline_date", "display_date", "reference_url"]

class StoryAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(Person, NodeAdmin, ordering=['name'])
admin.site.register(Concept, NodeAdmin, ordering=['name'])
admin.site.register(Object, NodeAdmin, ordering=['name'])
admin.site.register(Event, NodeAdmin, ordering=['name'])
admin.site.register(StoryContent, NodeAdmin, ordering=['name'])

admin.site.register(ExternalLink)

admin.site.register(Story, StoryAdmin)
