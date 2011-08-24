from django.views.generic import TemplateView, FormView
from django.http import HttpResponse, Http404
from core.models import Object, Person, Event, Concept, Edge
from core.forms import EdgeForm


class EdgeEdit(TemplateView):
    """
    A view that allows us to edit.
    """

    template_name = "edge_editor/edge.html"

    def get_context_data(self, pk=None):
        try:
            edge = Edge.objects.get(pk=pk)
        except Edge.DoesNotExist:
            raise Http404

        return {"edge_id": pk}

class EdgeCreate(FormView):
    """
    A view for createing Edges
    """

    template_name = "edge_editor/edge.html"
    form_class = EdgeForm
