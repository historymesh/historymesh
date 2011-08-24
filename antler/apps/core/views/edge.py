from django.views.generic import TemplateView, FormView
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from core.models import Object, Person, Event, Concept, Edge
from core.forms import EdgeForm


class EdgeView(TemplateView):
    template_name = "edge_editor/edge_list.html"

    def get_context_data(self):
        return {
            "edges" : Edge.objects.order_by("id"),
        }


class EdgeEdit(FormView):
    """
    A view that allows us to edit.
    """

    def get_initial(self):
        edge = Edge.objects.get(pk=self.kwargs['pk'])
        return {
            "verb": edge.verb,
            "object" : edge.object.select_tuple[0],
            "subject" : edge.subject.select_tuple[0],
        }

    template_name = "edge_editor/edge.html"
    form_class = EdgeForm

    def form_valid(self, form):
        edge = Edge.objects.get(pk=self.kwargs['pk'])
        edge.verb = form.cleaned_data['verb']
        edge.subject = form.cleaned_data['subject']
        edge.object = form.cleaned_data['object']
        edge.save()
        return redirect('edge', pk=edge.id)


class EdgeCreate(FormView):
    """
    A view for creating Edges
    """

    template_name = "edge_editor/edge.html"
    form_class = EdgeForm

    def form_valid(self, form):
        edge = Edge()
        edge.verb = form.cleaned_data['verb']
        edge.subject = form.cleaned_data['subject']
        edge.object = form.cleaned_data['object']
        edge.save()
        return redirect('edge', pk=edge.id)