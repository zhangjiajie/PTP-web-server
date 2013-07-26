from django.conf.urls import patterns, url

from ptp import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^ptp/$', views.ptp_index, name='ptp_index'),
)