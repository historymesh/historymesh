from django.views.generic.base import TemplateView 
from core.models import Person, Concept, Event, Object
from django.shortcuts import get_object_or_404


class NodeView(TemplateView):
    
    def model_name(self):
        return self.model._meta.object_name.lower()
    
    def get_template_names(self):
        return "nodes/%s.html" % self.model_name()
    
    def get_context_data(self, pk):
        instance = get_object_or_404(self.model, pk=pk)
        
        return {
                self.model_name():instance,
                "incoming":instance.incoming().by_verb(),
                "outgoing":instance.outgoing().by_verb(),
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

