# -*- coding:utf-8 -*-
from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _


def home_page(request):
    messages.success(request, _(u'<strong>Welcome!</strong> This is a demo shop built on Satchless. Enjoy!'))
    return TemplateResponse(request, 'core/home_page.html')
