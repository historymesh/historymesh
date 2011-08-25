from django.views.generic import TemplateView
from core.models import Story
from core.views.layout import get_layout_data

class HomepageView(TemplateView):
    template_name = 'homepage.html'
    
    def get_context_data(self):
        context = get_layout_data()
        context['stories'] = Story.objects.filter(
            featured=True,
            edges__id__isnull=False,
        ).distinct()
        return context
