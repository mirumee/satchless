from ....payment.models import PaymentVariant
from django.db import models

class PaymentsGatewayReceipt(models.Model):
    pg_response_type = models.CharField(max_length=10, blank=True, null=True)
    pg_response_code = models.CharField(max_length=10, blank=True, null=True)
    pg_response_description = models.CharField(max_length=100, blank=True,
                                               null=True)
    pg_authorization_code = models.CharField(max_length=100, blank=True,
                                             null=True)
    pg_trace_number = models.CharField(max_length=50, blank=True, null=True)
    pg_merchant_id = models.CharField(max_length=10, blank=True, null=True)
    pg_transaction_type = models.CharField(max_length=10, blank=True,
                                           null=True)
    pg_total_amount = models.CharField(max_length=10, blank=True, null=True)
    pg_client_id = models.CharField(max_length=10, blank=True, null=True)
    other_error = models.CharField(max_length=100, blank=True, null=True)

class PaymentsGatewayVariant(PaymentVariant):
    pg_client_token = models.CharField(max_length=50, blank=True, null=True)
    pg_payment_token = models.CharField(max_length=50, blank=True, null=True)
    receipt = models.ForeignKey(PaymentsGatewayReceipt, blank=True, null=True)
