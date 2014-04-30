from django.conf.urls import patterns, url
from mirrors import views

urlpatterns = patterns('mirrors.views',
    url(r'^component$',
        views.ComponentList.as_view(),
        name='component-list'),
    url(r'^component/(?P<component>[-\w]+)$',
        views.ComponentDetail.as_view(),
        name='component-detail'),
     url(r'^component/(?P<component>[-\w]+)/attribute$',
         views.ComponentAttributeList.as_view(),
         name='component-attribute-list'),
    url(r'^component/(?P<component>[-\w]+)/attribute/(?P<attr_name>[-\w_]+)$',
        views.ComponentAttributeDetail.as_view(),
        name='component-attribute-detail'),
    url(r'^component/(?P<component>[-\w]+)/data$',
        views.component_data_uri,
        name='component-data-uri'),
    url(r'^schemas$',
        views.component_schemas,
        name='component-schemas'),
)
