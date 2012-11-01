from django.db import models


class StripeReceipt(models.Model):
    """
    Removed all validation as we want to log whatever we get back from Stripe
    no matter how mis-formed or broken.
    """
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    stripe_card_id = models.CharField(max_length=50, blank=True, null=True)

    # when making a card charge
    description = models.TextField(blank=True, null=True)

    # when making a customer charge
    customer = models.CharField(max_length=50, blank=True, null=True)

    fee = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)   # starts as timestamp
    refunded = models.NullBooleanField(blank=True, null=True)
    livemode = models.NullBooleanField(blank=True, null=True)
    currency = models.CharField(max_length=5, blank=True, null=True)    # usd
    amount = models.IntegerField(blank=True, null=True)     # in cents
    paid = models.NullBooleanField(blank=True, null=True)
    token = models.CharField(max_length=50, blank=True, null=True)  # "id"
    country = models.CharField(max_length=5, blank=True, null=True)
    cvc_check = models.CharField(max_length=5, blank=True, null=True)
    exp_month = models.IntegerField(blank=True, null=True)
    exp_year = models.IntegerField(blank=True, null=True)
    last4 = models.CharField(max_length=4, blank=True, null=True)
    card_type = models.CharField(max_length=50, blank=True, null=True)  # "type"

    class Meta:
        abstract = True
