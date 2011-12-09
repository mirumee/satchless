# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ProductPrice'
        db.create_table('simpleqty_productprice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True)),
            ('qty_mode', self.gf('django.db.models.fields.CharField')(default='variant', max_length=10)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=4)),
        ))
        db.send_create_signal('simpleqty', ['ProductPrice'])

        # Adding model 'PriceQtyOverride'
        db.create_table('simpleqty_priceqtyoverride', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_price', self.gf('django.db.models.fields.related.ForeignKey')(related_name='qty_overrides', to=orm['simpleqty.ProductPrice'])),
            ('min_qty', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=4)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=4)),
        ))
        db.send_create_signal('simpleqty', ['PriceQtyOverride'])

        # Adding model 'VariantPriceOffset'
        db.create_table('simpleqty_variantpriceoffset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_price', self.gf('django.db.models.fields.related.ForeignKey')(related_name='offsets', to=orm['simpleqty.ProductPrice'])),
            ('variant', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Variant'], unique=True)),
            ('price_offset', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=4)),
        ))
        db.send_create_signal('simpleqty', ['VariantPriceOffset'])


    def backwards(self, orm):
        
        # Deleting model 'ProductPrice'
        db.delete_table('simpleqty_productprice')

        # Deleting model 'PriceQtyOverride'
        db.delete_table('simpleqty_priceqtyoverride')

        # Deleting model 'VariantPriceOffset'
        db.delete_table('simpleqty_variantpriceoffset')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'product.product': {
            'Meta': {'object_name': 'Product'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '80', 'db_index': 'True'})
        },
        'product.variant': {
            'Meta': {'object_name': 'Variant'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sku': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'})
        },
        'simpleqty.priceqtyoverride': {
            'Meta': {'ordering': "('min_qty',)", 'object_name': 'PriceQtyOverride'},
            'base_price': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'qty_overrides'", 'to': "orm['simpleqty.ProductPrice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_qty': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '4'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '4'})
        },
        'simpleqty.productprice': {
            'Meta': {'object_name': 'ProductPrice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '4'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True'}),
            'qty_mode': ('django.db.models.fields.CharField', [], {'default': "'variant'", 'max_length': '10'})
        },
        'simpleqty.variantpriceoffset': {
            'Meta': {'object_name': 'VariantPriceOffset'},
            'base_price': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offsets'", 'to': "orm['simpleqty.ProductPrice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price_offset': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '4'}),
            'variant': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Variant']", 'unique': 'True'})
        }
    }

    complete_apps = ['simpleqty']
