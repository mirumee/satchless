from ....payment.models import PaymentVariant
from django.db import models

class PaymentsGatewayReceipt(models.Model):
    pg_merchant_id = models.CharField(blank=True, null=True, max_length=10)
    pg_transaction_type = models.CharField(blank=True, null=True,
                                           max_length=10)

    pg_merchant_data_1 = models.CharField(blank=True, null=True, max_length=50)
    pg_merchant_data_2 = models.CharField(blank=True, null=True, max_length=50)
    pg_merchant_data_3 = models.CharField(blank=True, null=True, max_length=50)
    pg_merchant_data_4 = models.CharField(blank=True, null=True, max_length=50)
    pg_merchant_data_5 = models.CharField(blank=True, null=True, max_length=50)
    pg_merchant_data_6 = models.CharField(blank=True, null=True, max_length=50)
    pg_merchant_data_7 = models.CharField(blank=True, null=True, max_length=50)
    pg_merchant_data_8 = models.CharField(blank=True, null=True, max_length=50)
    pg_merchant_data_9 = models.CharField(blank=True, null=True, max_length=50)

    pg_total_amount = models.CharField(blank=True, null=True, max_length=10)
    pg_sales_tax_amount = models.CharField(blank=True, null=True,
                                           max_length=10)

    pg_consumer_id = models.CharField(blank=True, null=True, max_length=20)
    ecom_consumerorderid = models.CharField(blank=True, null=True,
                                            max_length=20)
    ecom_walletid = models.CharField(blank=True, null=True, max_length=20)
    ecom_billto_postal_name_first = models.CharField(blank=True, null=True,
                                                     max_length=30)
    ecom_billto_postal_name_last = models.CharField(blank=True, null=True,
                                                    max_length=30)
    pg_billto_postal_name_company = models.CharField(blank=True, null=True,
                                                     max_length=30)
    ecom_billto_online_email = models.CharField(blank=True, null=True,
                                                max_length=50)

    pg_response_type = models.CharField(blank=True, null=True, max_length=10)
    pg_response_code = models.CharField(blank=True, null=True, max_length=10)
    pg_response_description = models.CharField(blank=True, null=True,
                                               max_length=100)
    pg_avs_result = models.CharField(blank=True, null=True, max_length=10)
    pg_trace_number = models.CharField(blank=True, null=True, max_length=50)
    pg_authorization_code = models.CharField(blank=True, null=True,
                                             max_length=100)
    pg_preauth_result = models.CharField(blank=True, null=True, max_length=10)
    pg_preauth_description = models.CharField(blank=True, null=True,
                                              max_length=100)
    pg_cvv2_result = models.CharField(blank=True, null=True, max_length=10)
    pg_3d_secure_result = models.CharField(blank=True, null=True,
                                           max_length=10)

    pg_client_id = models.CharField(max_length=10, blank=True, null=True)
    other_error = models.CharField(max_length=100, blank=True, null=True)

class PaymentsGatewayVariant(PaymentVariant):
    pg_client_token = models.CharField(max_length=50, blank=True, null=True)
    pg_payment_token = models.CharField(max_length=50, blank=True, null=True)
    token_first_name = models.CharField(max_length=50, blank=True, null=True)
    token_last_name = models.CharField(max_length=50, blank=True, null=True)
    receipt = models.ForeignKey(PaymentsGatewayReceipt, blank=True, null=True)
