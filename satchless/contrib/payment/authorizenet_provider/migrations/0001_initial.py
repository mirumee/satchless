# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AuthorizeNetVariant'
        db.create_table('authorizenet_provider_authorizenetvariant', (
            ('paymentvariant_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['payment.PaymentVariant'], unique=True, primary_key=True)),
            ('cc_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('cc_number', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('cc_expiration', self.gf('django.db.models.fields.DateField')(null=True)),
            ('cc_cvv2', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('billing_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('response', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authorizenet.Response'], null=True, blank=True)),
        ))
        db.send_create_signal('authorizenet_provider', ['AuthorizeNetVariant'])


    def backwards(self, orm):
        
        # Deleting model 'AuthorizeNetVariant'
        db.delete_table('authorizenet_provider_authorizenetvariant')


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
        'authorizenet.response': {
            'MD5_Hash': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Meta': {'object_name': 'Response'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'amount': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'auth_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'avs_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'cavv_response': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'cust_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'cvv2_resp_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'duty': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'freight': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_num': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'po_num': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'response_code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'response_reason_code': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'response_reason_text': ('django.db.models.fields.TextField', [], {}),
            'response_subcode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'ship_to_address': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'ship_to_city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'ship_to_company': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_country': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'ship_to_first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_state': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'ship_to_zip': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'tax': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'tax_exempt': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'test_request': ('django.db.models.fields.CharField', [], {'default': "'FALSE'", 'max_length': '10', 'blank': 'True'}),
            'trans_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'authorizenet_provider.authorizenetvariant': {
            'Meta': {'object_name': 'AuthorizeNetVariant', '_ormbases': ['payment.PaymentVariant']},
            'billing_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'cc_cvv2': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'cc_expiration': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'cc_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'cc_number': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'paymentvariant_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['payment.PaymentVariant']", 'unique': 'True', 'primary_key': 'True'}),
            'response': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authorizenet.Response']", 'null': 'True', 'blank': 'True'})
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
        'payment.paymentvariant': {
            'Meta': {'object_name': 'PaymentVariant'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'order': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['order.Order']", 'unique': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '4'})
        }
    }

    complete_apps = ['authorizenet_provider']
