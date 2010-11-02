from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
        (r'^$', views.my_contact),
        (r'^address/new/', views.address_edit),
        (r'^address/(?P<address_pk>[0-9]+)/edit/', views.address_edit),
        )
