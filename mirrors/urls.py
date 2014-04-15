from django.conf.urls import patterns, url
from mirrors import views

urlpatterns = patterns('mirrors.views',
                       url(r'^component$',
                           views.ComponentList.as_view(),
                           name='component-list'),
                       url(r'^component/(?P<slug>[-\w]+)$',
                           views.ComponentDetail.as_view(),
                           name='component-detail'),
                       url(r'^component/(?P<slug>[-\w]+)/data$',
                           views.component_data_uri,
                           name='component-data-uri'))
