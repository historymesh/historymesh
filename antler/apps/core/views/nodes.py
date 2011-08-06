from django.views.generic.base import TemplateView 

class PersonView(TemplateView):

    template_name = "nodes/person.html"

