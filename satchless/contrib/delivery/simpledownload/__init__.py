from django.utils.translation import ugettext

from ....delivery import DeliveryProvider, DeliveryType


class DownloadDeliveryProvider(DeliveryProvider):
    def __unicode__(self):
        return ugettext("Download delivery")

    def enum_types(self, customer=None, delivery_group=None):
        if not delivery_group or not delivery_group.require_shipping_address:
            yield DeliveryType(provider=self, typ='SimpleDownload', name='Download')


    def save(self, delivery_group, typ, form):
        delivery_group.delivery_type_name = 'download'
        delivery_group.save()
