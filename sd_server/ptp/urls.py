from django.conf.urls import patterns, url
from django.conf import settings

from ptp import views

urlpatterns = patterns('',
    url(r'^$', views.ptp_index, name='ptp_index'),
    url(r'^ptp/$', views.ptp_index, name='ptp_index'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^findjob/$', views.findjob, name='findjob'),
    #url(r'^ptp/result/(\d+)$', views.show_ptp_result, name = 'result'),
    url(r'^ptp/result/$', views.show_ptp_result, name = 'result'),
    url(r'^download/(.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT}),
)
