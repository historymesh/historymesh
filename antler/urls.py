from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from core.views import importer, nodes

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^import/', importer.ImportView.as_view(), name="import"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^person/(?P<pk>\d+)/', nodes.PersonView.as_view(), name="person"),
)
