# -*- coding:utf-8 -*-
from django.views.generic.simple import direct_to_template


def home_page(request):
    return direct_to_template(request, 'core/home_page.html')
