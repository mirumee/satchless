# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PostShippingType'
        db.create_table('simplepost_postshippingtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('typ', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal('simplepost', ['PostShippingType'])

        # Adding model 'PostShippingVariant'
        db.create_table('simplepost_postshippingvariant', (
            ('deliveryvariant_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['delivery.DeliveryVariant'], unique=True, primary_key=True)),
            ('shipping_first_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('shipping_last_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('shipping_company_name', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('shipping_street_address_1', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('shipping_street_address_2', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('shipping_city', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('shipping_postal_code', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('shipping_country', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('shipping_country_area', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('shipping_phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
        ))
        db.send_create_signal('simplepost', ['PostShippingVariant'])


    def backwards(self, orm):
        
        # Deleting model 'PostShippingType'
        db.delete_table('simplepost_postshippingtype')

        # Deleting model 'PostShippingVariant'
        db.delete_table('simplepost_postshippingvariant')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cart.cart': {
            'Meta': {'object_name': 'Cart'},
            'currency': ('django.db.models.fields.CharField', [], {'default': "'GBP'", 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'carts'", 'null': 'True', 'to': "orm['auth.User']"}),
            'typ': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'delivery.deliveryvariant': {
            'Meta': {'object_name': 'DeliveryVariant'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['contenttypes.ContentType']"}),
            'delivery_group': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['order.DeliveryGroup']", 'unique': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '4'})
        },
        'order.deliverygroup': {
            'Meta': {'object_name': 'DeliveryGroup'},
            'delivery_type': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': "orm['order.Order']"})
        },
        'order.order': {
            'Meta': {'ordering': "('-last_status_change',)", 'object_name': 'Order'},
            'billing_city': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'billing_company_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'billing_country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'billing_country_area': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'billing_first_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'billing_last_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'billing_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'billing_postal_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'billing_street_address_1': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'billing_street_address_2': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'billing_tax_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders'", 'null': 'True', 'to': "orm['cart.Cart']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_status_change': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'payment_type': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'checkout'", 'max_length': '32'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'simplepost.postshippingtype': {
            'Meta': {'object_name': 'PostShippingType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'typ': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'simplepost.postshippingvariant': {
            'Meta': {'object_name': 'PostShippingVariant'},
            'deliveryvariant_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['delivery.DeliveryVariant']", 'unique': 'True', 'primary_key': 'True'}),
            'shipping_city': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'shipping_company_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'shipping_country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'shipping_country_area': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'shipping_first_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'shipping_last_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'shipping_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'shipping_postal_code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'shipping_street_address_1': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'shipping_street_address_2': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        }
    }

    complete_apps = ['simplepost']
