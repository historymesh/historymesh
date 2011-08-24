from django.views.generic.base import TemplateView 
from core.models import Person, Concept, Event, Object, Story
from django.shortcuts import get_object_or_404


class NodeView(TemplateView):
    template_name = 'nodes/show.html'

    def model_name(self):
        return self.model._meta.object_name.lower()
    
    def get_context_data(self, slug):
        instance = get_object_or_404(self.model, slug=slug)

        try:
            story_slug = self.request.GET.get('story')
            story = Story.objects.get(slug=story_slug)
            story.set_current_node(instance)
        except Story.DoesNotExist:
            story = None

        story_content = instance.outgoing('described_by')
        current_story_content = story_content.filter(story=story).follow()
        other_story_content = story_content.exclude(story=story).follow()

        outgoing_primary = instance.outgoing('primary')
        story_next = outgoing_primary.filter(story=story).follow()
        if len(story_next) > 0:
            story_next = story_next[0]

        incoming_primary = instance.incoming('primary')
        story_prev = incoming_primary.filter(story=story).follow()
        if len(story_prev) > 0:
            story_prev = story_prev[0]

        return {
            "subject": instance,
            "incoming": instance.incoming().by_verb(),
            "outgoing": instance.outgoing().by_verb(),
            "story": story,
            "other_story_content": other_story_content,
            "current_story_content": current_story_content,
        }


class PersonView(NodeView):
    model = Person

        
class EventView(NodeView):
    model = Event

        
class ConceptView(NodeView):
    model = Concept


class ObjectView(NodeView):
    model = Object


class NodeIndexView(TemplateView):
    template_name = 'nodes/index.html'

    def get_context_data(self):
        return {
            'people': Person.objects.order_by('timeline_date'),
            'events': Event.objects.order_by('timeline_date'),
            'concepts': Concept.objects.order_by('timeline_date'),
            'objects': Object.objects.order_by('timeline_date'),
        }

