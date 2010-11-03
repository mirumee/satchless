from django.conf.urls.defaults import *
from . import views

urlpatterns = patterns('',
        url(r'^$', views.my_contact, name='satchless-contact-my_contact'),
        url(r'^address/new/', views.address_edit, name='satchless-contact-address_new'),
        url(r'^address/(?P<address_pk>[0-9]+)/edit/',
            views.address_edit, name='satchless-contact-address_edit'),
        )
