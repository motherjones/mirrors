from django.conf.urls import patterns, url

urlpatterns = patterns(
    'mirrors.views',
    url(r'^(?P<slug>[-\w]+)$', 'get_component'),
    url(r'^(?P<slug>[-\w]+)/data$', 'get_component_data'),
    url(r'^(?P<slug>[-\w]+)/revision/(?P<revision>\d+)$',
        'get_component_revision'),
    url(r'^(?P<slug>[-\w]+)/revision/(?P<revision>\d+)/data$',
        'get_component_revision_data'),
)
