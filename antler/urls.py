from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from core.views import importer, nodes

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^import/', importer.ImportView.as_view(), name="import"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^person/(?P<pk>\d+)/', nodes.PersonView.as_view(), name="person"),
    url(r'^concept/(?P<pk>\d+)/', nodes.ConceptView.as_view(), name="concept"),
    url(r'^event/(?P<pk>\d+)/', nodes.EventView.as_view(), name="event"),
    url(r'^object/(?P<pk>\d+)/', nodes.ObjectView.as_view(), name="object"),
)
