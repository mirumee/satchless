.. _checkout-payment:

=======
Payment
=======

Satchless is designed to work with any payments application which is at least a
little bit portable. Usually, a piece of *glue* would be required, namely a
``satchless.payment.PaymentProvider`` subclass implementing API to work with
Satchless checkout.

Payment provider
----------------

Payment providers should be added to setting named
``SATCHLESS_PAYMENT_PROVIDERS``. This sequence is being iterated over to query
for available payment methods and for details forms, much in the way the
:ref:`delivery providers <checkout-delivery-providers>` are asked.

Confirmation form
.................

Every payment provider should implement a confirmation form, which includes
all the order's details and additional info ready to be processed by the
payment gateway.

This form is being shown at the last step of the checkout. By default,
satchless shows complete information about the order and asks the customer to
review and confirm it. Clicking the *confirm* button would proceed to the
payment gateway.

.. note::
   Satchless allows the confirmation form to carry information about the method
   used to send the data, so even ``GET`` requests could be handled there.

Example of payments provider
............................

In ``satchless.contrib.payment.django_payments_provider`` you may find an
example, working implementation of a paymnt provider, using `django-payments`_
as a backend.

.. _`django-payments`: https://github.com/mirumee/django-payments
