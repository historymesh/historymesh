from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from core.views import importer, nodes, layout
from search.views import SearchView
from homepage.views import HomepageView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', HomepageView.as_view(), name='homepage'),
    url(r'^import/', importer.ImportView.as_view(), name="import"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^person/(?P<slug>[a-z0-9-]+)/$', nodes.PersonView.as_view(), name="person"),
    url(r'^concept/(?P<slug>[a-z0-9-]+)/$', nodes.ConceptView.as_view(), name="concept"),
    url(r'^event/(?P<slug>[a-z0-9-]+)/$', nodes.EventView.as_view(), name="event"),
    url(r'^object/(?P<slug>[a-z0-9-]+)/$', nodes.ObjectView.as_view(), name="object"),
    url(r'^random$', nodes.RandomNodeView.as_view(), name="random-node"),
    url(r'^layout/$', layout.LayoutView.as_view()),
    url(r'^layout/image/$', layout.LayoutImage.as_view()),
    url(r'^overview/$', nodes.NodeIndexView.as_view()),
    url(r'^map/$', layout.MapView.as_view(), name="map"),
    url(r'^search/$', SearchView.as_view(), name="search"),
    url(r'^about$', TemplateView.as_view(template_name="about.html"), name="about-page"),
)

if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^static/(?P<path>.*)$', 
            'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$', 
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
