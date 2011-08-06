from django.views.generic.base import TemplateView 
from core.models import Person, Concept, Event, Object
from django.shortcuts import get_object_or_404

class PersonView(TemplateView):

    template_name = "nodes/person.html"

    def get_context_data(self, pk):
        person = get_object_or_404(Person, pk=pk)
        return {
                "person":person,
               }
        
        
class EventView(TemplateView):
    
    template_name = "nodes/event.html"
    
    def get_context_data(self, pk):
        event = get_object_or_404(Event, pk=pk)
        return {
                "event":event,
               }

        
class ConceptView(TemplateView):
    
    template_name = "nodes/concept.html"
    
    def get_context_data(self, pk):
        concept = get_object_or_404(Concept, pk=pk)
        return {
                "concept":concept,
               }


class ObjectView(TemplateView):
    
    template_name = "nodes/object.html"
    
    def get_context_data(self, pk):
        object = get_object_or_404(Object, pk=pk)
        return {
                "object":object,
               }
        