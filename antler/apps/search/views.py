from django.views.generic import TemplateView
import core.models
from django.shortcuts import get_object_or_404

# Lookup for object classes based on their types, done explicitly to ensure
# that data pointing to the wrong type in the search engine index causes an
# error quickly.
valid_object_types = { }
def _add_object_type(klass):
    valid_object_types[klass._meta.object_name] = klass
_add_object_type(core.models.Person)
_add_object_type(core.models.Concept)
_add_object_type(core.models.Event)
_add_object_type(core.models.Object)
_add_object_type(core.models.Story)

class SearchView(TemplateView):
    template_name = 'search/search.html'
    
    def get_context_data(self):
        # This sometimes explodes, so moved in here.
        from search.utils import build_query
        query_string = self.request.GET.get('q')
        query = build_query(query_string)
        return {
            'results': query,
            'query_string': query_string,
        }
