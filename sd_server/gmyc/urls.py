from django.conf.urls import patterns, url
from django.conf import settings

from gmyc import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^gmyc/$', views.gmyc_index, name='ptp_index'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^gmyc/result/(\d+)$', views.show_gmyc_result, name = 'result'),
    url(r'^download/(.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT}),
)
