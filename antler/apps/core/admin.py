from django.contrib import admin
from core.models import Edge, Person, Concept, Object, Event, StoryContent, ExternalLink, Story, Image
from core.forms import EdgeAdminForm, StoryContentAdminForm

admin.site.register(
    Edge,
    list_display=[
        'id',
        'story',
        'linked_subject',
        'verb',
        'linked_object',
    ],
    list_filter = [
        'subject_type',
        'object_type',
        'verb',
        'story',
    ],
    form = EdgeAdminForm,
)

class NodeAdmin(admin.ModelAdmin):
    list_display = ["name", "timeline_date", "display_date", "reference_url"]
    list_editable = ["timeline_date", "display_date", "reference_url"]
    ordering = ['name']

class StoryAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(Person, NodeAdmin)
admin.site.register(Concept, NodeAdmin)
admin.site.register(Object, NodeAdmin)
admin.site.register(Event, NodeAdmin)
admin.site.register(
    StoryContent,
    list_display = ["story"],
    form = StoryContentAdminForm,
)

admin.site.register(ExternalLink, list_display=["name", "url"])
admin.site.register(Image, list_display=["id", "image", "caption"])

admin.site.register(Story, StoryAdmin)
