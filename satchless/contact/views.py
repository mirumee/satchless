from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from . import models

@login_required
def my_contact(request):
    customer = models.Customer.objects.get_or_create_for_user(request.user)
    return direct_to_template(request,
            'satchless/contact/my_contact.html',
            {'customer': customer})

@login_required
def address_edit(request, address_pk=None):
    if address_pk:
        address = get_object_or_404(user=request.user, pk=address_pk)
    return direct_to_template(request,
            'satchless/contact/address_edit.html',
            {'form': form})
