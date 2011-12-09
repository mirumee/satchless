from django.db import models
from django.utils.translation import ugettext_lazy as _

# provides display names for the two-letter continent codes we got from geonames
CONTINENTS = (
    ('EU', _('Europe')),
    ('NA', _('North America')),
    ('SA', _('South America')),
    ('AS', _('Asia')),
    ('OC', _('Oceania')),
    ('AF', _('Africa')),
    ('AN', _('Antarctica')),
)

class PostShippingType(models.Model):
    typ = models.SlugField(_('slug'), max_length=50, unique=True,
                           help_text=_('Generated automatically from the name.'))
    region = models.ForeignKey('DeliveryRegion',
                               help_text=_('Which region is this delivery'
                                           ' option attached to?'))
    name = models.CharField(_('name'), max_length=128,
                            help_text=_("eg 'Standard', 'Next Day' etc."))
    description = models.CharField(max_length=64)
    description.help_text = "eg 'Usually delivered in 3-5 days.'"
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)

    class Meta:
        ordering = ('region','price',)
        verbose_name = _('Post shipping type')
        verbose_name_plural = _('Post shipping types')

    def __unicode__(self):
        return self.name

    def country_is_valid(self, country_code):
        try:
            country = DeliveryCountry.objects.get(code=country_code)
        except DeliveryCountry.DoesNotExist:
            return False
        else:
            if hasattr(country, 'region') and country.region == self.region:
                return True
            return False


class DeliveryCountryManager(models.Manager):
    def deliverable(self):
        return self.filter(region__isnull=False).order_by('name')


class DeliveryRegion(models.Model):
    name = models.CharField(_('name'), max_length=64)
    sort_weight = models.IntegerField(default=100,
                                      help_text=_("'Heavier' items will sink to"
                                                  " the bottom. Items with the"
                                                  " same weight will sort"
                                                  " alphabetically."))

    class Meta():
        ordering = ('sort_weight', 'name',)

    def __unicode__(self):
        return self.name


class DeliveryCountry(models.Model):
    """
    Delivery destination countries

    To populate run:

        ./manage.py importcountries
    """
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(_('name'), max_length=64)
    continent = models.CharField(max_length=2, choices=CONTINENTS,
                                 help_text = _('From the geonames src data.'
                                               ' May be useful in assigning'
                                               ' countries to regions. Not'
                                               ' used by the delivery system.'))
    region = models.ForeignKey(DeliveryRegion, verbose_name='Delivery Region',
                               blank=True, null=True, on_delete=models.SET_NULL,
                               help_text=_('This country will not be'
                                           ' available for delivery if no'
                                           ' region is chosen.'))
    promote = models.BooleanField(default=False,
                                  help_text=_('Promote this country to the'
                                              ' top of country select lists,'
                                              ' eg in address forms.'
                                              ' (Otherwise countries are'
                                              ' grouped by region).'))
    sort_weight = models.IntegerField(default=100,
                                      help_text=_("'Heavier' items will sink to"
                                                  " the bottom. Items with the"
                                                  " same weight will sort"
                                                  " alphabetically."))
    objects = DeliveryCountryManager()

    class Meta():
        ordering = ('-promote', 'region', 'sort_weight', 'name',)
        verbose_name_plural = 'Delivery countries'

    def __unicode__(self):
        return self.name