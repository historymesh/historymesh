from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from core.views import importer

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^import/', importer.ImportView.as_view(), name="import"),
    url(r'^admin/', include(admin.site.urls)),
)
