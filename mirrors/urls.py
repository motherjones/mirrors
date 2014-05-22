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
    url(r'^component/(?P<slug>[-\w]+)/attribute$',
        views.ComponentAttributeList.as_view(),
        name='component-attribute-list'),
    url(r'^component/(?P<slug>[-\w]+)/attribute/(?P<name>[-\w_]+)$',
        views.ComponentAttributeDetail.as_view(),
        name='component-attribute-detail'),
    url(r'^component/(?P<slug>[-\w]+)/data$',
        views.ComponentData.as_view(),
        name='component-data'),
    url(r'^schemas$',
        views.component_schemas,
        name='component-schemas')
)
# url(r'^component/(?P<slug>[-\w]+)/attribute/(?P<attr_name>[-\w_]+)/(?P<index>[\d]+)$',
#     views.ComponentAttributeDetail.as_view(),
#     name='component-attribute-detail'),
