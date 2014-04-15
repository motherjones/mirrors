from django.conf.urls import patterns, include, url
from django.contrib import admin
from mirrors import urls as mirrors_urls

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mirrors_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^mirrors/', include(mirrors_urls)), 
    url(r'^admin/', include(admin.site.urls)),
)
