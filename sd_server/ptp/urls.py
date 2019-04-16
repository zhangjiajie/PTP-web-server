import django
from django.conf.urls import url
from django.conf import settings

from ptp import views

urlpatterns = [
    url(r'^$', views.ptp_index, name='ptp_index'),
    url(r'^ptp/$', views.ptp_index, name='ptp_index'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^findjob/$', views.findjob, name='findjob'),
    url(r'^help/$', views.help1, name='help'),
    url(r'^ptp/result/$', views.show_ptp_result, name = 'result'),
    url(r'^ptp/phylomap/$', views.show_phylomap_result, name = 'phylomap'),
    url(r'^download/(.*)$', django.views.static.serve, {'document_root':settings.MEDIA_ROOT}),
]
