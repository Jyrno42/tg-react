from __future__ import unicode_literals

from django.conf.urls import include, url

from django.contrib import admin

admin.autodiscover()


urlpatterns = [
    include(admin.site.urls),
]
