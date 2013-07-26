from django.conf.urls import patterns, url

from ptp import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)