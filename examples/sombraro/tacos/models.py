from django.db import models

# satchless abstract classes
from satcheless.image.models import Image # uses settings.py to determine sizes
from satchless.product.models import ProductAbstract, Variant, Product

# for localization support
from django.utils.translation import ugettext as _

class ProductImage(Image):
    product = models.ForeignKey(Product, related_name="images")
    caption = models.CharField(_("Caption"), max_length=128, blank=True)
    order = models.PositiveIntegerField(blank=True)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return os.path.basename(self.image.name)

    def save(self, *args, **kwargs):
        """
        automatically adds an ordering to the saved image
        """
        if self.order is None:
            self.order = self.product.images.aggregate(max_order=models.Max("order"))['max_order'] or 0
        return super(ProductImage, self).save(*args, **kwargs)

class Product(ProductAbstract):
    """
    Here we define the base model for our store's products. This is where
    additional meta-data (such as creation date and model) can be added.
    """
    main_image = models.ForeignKey(ProductImage, null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text=_("Main product image (first image by default)"))

    class Meta:
        abstract = True

class Taco(Product):
    """
    FINALLY! The money-maker. The taco.
    """
    class Meta:
        verbose_name = _("Taco")
        verbose_name_plural = _("Tacos")
    # wasn't that easy? :)
    # As I said, the important logic is mostly stored in the variants

class TacoVariant(Variant):
    """
    Assuming these tacos are served in the US, we'll want to make sure to not
    add a "small" variant. Instead, we'll assume that no one wants a small
    taco.
    """
    product = models.ForeignKey(Taco, related_name="variants")
    SIZE_CHOICES = (
        ('regular', _("Regular")),
        ('large', _("Large")),
        ('supreme', _("Supreme")),
    )
    size = models.CharField(max_length=32, choices=SIZE_CHOICES)
    class Meta:
        abstract = True

# SIGNALS
"""
    Signals are used for assigning the main image to the product. If you'd
    like, you can also put them in a file called "listeners.py" as long as you
    add the following to this apps' __init__.py file:
        import listeners
"""

def assign_main_image(sender, instance, **kwargs):
    if not kwargs.get('raw', False) and instance.product.main_image == None \
            and instance.product.images.exists():
        instance.product.main_image = instance.product.images.all()[0]
        instance.product.save()
models.signals.post_save.connect(assign_main_image, sender=ProductImage)

def assign_new_main_image(sender, instance, **kwargs):
    try:
        if instance.product.main_image == instance and instance.product.images.exists():
            instance.product.main_image = instance.product.images.all()[0]
            instance.product.save()
    except Product.DoesNotExist:
        pass
models.signals.post_delete.connect(assign_new_main_image, sender=ProductImage)
