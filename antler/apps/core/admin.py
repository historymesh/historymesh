from django.contrib import admin
from core.models import Edge, Person, Concept, Object, Event, StoryContent, ExternalLink, Story

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

class StoryAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(Person, NodeAdmin)
admin.site.register(Concept, NodeAdmin)
admin.site.register(Object, NodeAdmin)
admin.site.register(Event, NodeAdmin)
admin.site.register(StoryContent, NodeAdmin)

admin.site.register(ExternalLink)

admin.site.register(Story, StoryAdmin)
