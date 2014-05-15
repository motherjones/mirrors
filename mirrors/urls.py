from django.conf.urls import patterns, url
from mirrors import views

urlpatterns = patterns(
    'mirrors.views',
    url(r'^component$',
        views.ComponentList.as_view(),
        name='component-list'),
    url(r'^component/(?P<slug>[-\w]+)$',
        views.ComponentDetail.as_view(),
        name='component-detail'),
    url(r'^component/(?P<slug>[-\w]+)/data$',
        views.ComponentData.as_view(),
        name='component-data'),
    url(r'^component/(?P<slug>[-\w]+)/lock$',
        views.ComponentLock.as_view(),
        name='component-lock'),
    url(r'^schemas$',
        views.component_schemas,
        name='component-schemas')
)
