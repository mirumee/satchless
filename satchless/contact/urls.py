from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
        (r'^$', views.my_contact),
        url(r'^address/new/', views.address_edit, name='satchless.contact.views.address_new'),
        (r'^address/(?P<address_pk>[0-9]+)/edit/', views.address_edit),
        )
