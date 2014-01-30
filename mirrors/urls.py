from django.conf.urls import patterns, url

urlpatterns = patterns(
    'content.views',
    url(r'^(?P<ver>[-.\d+])/(?P<slug>[-\w]+)$', 'get_content'),
    url(r'^(?P<ver>[-.\d+])/(?P<slug>[-\w]+)/data$', 'get_content_data'),
    url(r'^(?P<ver>[-.\d+])/(?P<slug>[-\w]+)/revision/(?P<revision>\d+)$',
        'get_content_revision'),
    url(r'^(?P<ver>[-.\d+])/(?P<slug>[-\w]+)/revision/(?P<revision>\d+)/data$',
        'get_content_revision_data'),
)
