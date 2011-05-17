from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from . import models
from . import forms

@login_required
def my_contact(request):
    customer = models.Customer.objects.get_or_create_for_user(request.user)
    return TemplateResponse(request, 'satchless/contact/my_contact.html', {
        'customer': customer,
    })

@login_required
def address_edit(request, address_pk=None,
                 formclass=forms.AddressFormWithDefaultCheckboxes):
    if address_pk:
        address = get_object_or_404(models.Address, customer__user=request.user,
                                    pk=address_pk)
    else:
        address = None
    if request.method == 'POST':
        form = formclass(instance=address, data=request.POST)
        if form.is_valid():
            user = request.user
            customer = models.Customer.objects.get_or_create_for_user(user)
            form.instance.customer = customer
            form.save()
            return redirect('satchless-contact-my-contact')
    else:
        form = formclass(instance=address)
    return TemplateResponse(request, 'satchless/contact/address_edit.html', {
        'address': address,
        'form': form,
    })
