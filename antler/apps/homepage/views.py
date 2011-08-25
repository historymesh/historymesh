from django.views.generic import TemplateView
from core.models import Story


class HomepageView(TemplateView):
    template_name = 'homepage.html'
    
    def get_context_data(self):
        return {
            'stories': Story.objects.filter(featured=True)
        }
