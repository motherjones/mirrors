from django.conf.urls import patterns, url
from mirrors import views

urlpatterns = patterns('mirrors.views',
    url(r'^component/(?P<slug>[-\w]+)$', 
        views.ComponentDetail.as_view(),
        name='component-detail'),
)
