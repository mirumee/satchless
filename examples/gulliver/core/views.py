# -*- coding:utf-8 -*-
from django.contrib import messages
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _


def home_page(request):
    messages.success(request, _(u'<strong>Welcome!</strong> This is a demo shop built on Satchless. Enjoy!'))
    return direct_to_template(request, 'core/home_page.html')
