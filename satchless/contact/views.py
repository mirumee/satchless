from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from . import models
from . import forms

@login_required
def my_contact(request):
    customer = models.Customer.objects.get_or_create_for_user(request.user)
    return direct_to_template(request,
            'satchless/contact/my_contact.html',
            {'customer': customer})

@login_required
def address_edit(request, address_pk=None, formclass=forms.AddressFormWithDefaultCheckboxes):
    if address_pk:
        address = get_object_or_404(models.Address, customer__user=request.user, pk=address_pk)
    else:
        address = None
    if request.method == 'POST':
        form = formclass(instance=address, data=request.POST)
        if form.is_valid():
            form.instance.customer = models.Customer.objects.get_or_create_for_user(request.user)
            form.save()
            return HttpResponseRedirect(reverse('satchless-contact-my_contact'))
    else:
        form = formclass(instance=address)
    return direct_to_template(request,
            'satchless/contact/address_edit.html',
            {'form': form, 'address': address})
