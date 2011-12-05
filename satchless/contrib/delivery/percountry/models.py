from django.db import models
from django.utils.translation import ugettext_lazy as _

from ....delivery.models import PhysicalShippingVariant



class PostShippingType(models.Model):
    typ = models.SlugField(_('slug'), max_length=50, unique=True)
    typ.help_text = "Generated automatically from the name."
    region = models.ForeignKey('DeliveryRegion')
    region.help_text = 'Which region is this delivery option attached to?'
    name = models.CharField(_('name'), max_length=128)
    name.help_text = "eg 'Standard', 'Next Day' etc"
    description = models.CharField(max_length=64)
    description.help_text = "eg 'Usually delivered in 3-5 days.'"
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)

    def country_is_valid(self, country_code):
        try:
            country = DeliveryCountry.objects.get(code=country_code)
        except DeliveryCountry.DoesNotExist:
            return False
        else:
            if hasattr(country, 'region') and country.region == self.region:
                return True
            return False

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('region','price',)
        verbose_name = _('Post shipping type')
        verbose_name_plural = _('Post shipping types')


class PostShippingVariant(PhysicalShippingVariant):
    pass


# provides display names for the two-letter continent codes we got from geonames
CONTINENTS = (
    ('EU','Europe'),
    ('NA','North America'),
    ('SA','South America'),
    ('AS','Asia'),
    ('OC','Oceania'),
    ('AF','Africa'),
    ('AN','Antarctica'),
)

class DeliveryCountryManager(models.Manager):
    def deliverable(self):
        return self.filter(region__isnull=False).order_by('name')

class DeliveryCountry(models.Model):
    """
    ./manage.py importcountries
    """
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(_('name'), max_length=64)
    continent = models.CharField(max_length=2, choices=CONTINENTS)
    continent.help_text = 'From the geonames src data. May be useful in assigning countries to regions. Not used by the delivery system.'
    region = models.ForeignKey(to='DeliveryRegion', verbose_name='Delivery Region', blank=True, null=True, on_delete=models.SET_NULL)
    region.help_text = 'This country will not be available for delivery if no region is chosen.'

    promote = models.BooleanField(default=False)
    promote.help_text = 'Promote this country to the top of country select lists, eg in address forms. (Otherwise countries are grouped by region).'
    sort_weight = models.IntegerField(default=100)
    sort_weight.help_text = "'Heavier' items will sink to the bottom. Items with the same weight will sort alphabetically."

    objects = DeliveryCountryManager()

    def __unicode__(self):
        return self.name

    class Meta():
        ordering = ('-promote','region','sort_weight','name',)
        verbose_name_plural = 'Delivery countries'



class DeliveryRegion(models.Model):
    name = models.CharField(_('name'), max_length=64)
    sort_weight = models.IntegerField(default=100)
    sort_weight.help_text = "'Heavier' items will sink to the bottom. Items with the same weight will sort alphabetically."

    def __unicode__(self):
        return self.name

    class Meta():
        ordering = ('sort_weight','name',)
