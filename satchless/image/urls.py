from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
    url(r'^thumbnail/(?P<image_id>\d+)/(?P<size>[^/]+)/$', views.thumbnail, name='satchless-image-thumbnail'),
)
