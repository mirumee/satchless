# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ProductSet'
        db.create_table('productset_productset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('productset', ['ProductSet'])

        # Adding model 'ProductSetItem'
        db.create_table('productset_productsetitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('productset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['productset.ProductSet'])),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Variant'])),
            ('sort', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('productset', ['ProductSetItem'])

        # Adding model 'ProductSetImage'
        db.create_table('productset_productsetimage', (
            ('image_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['image.Image'], unique=True, primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['productset.ProductSet'])),
            ('sort', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('productset', ['ProductSetImage'])


    def backwards(self, orm):
        
        # Deleting model 'ProductSet'
        db.delete_table('productset_productset')

        # Deleting model 'ProductSetItem'
        db.delete_table('productset_productsetitem')

        # Deleting model 'ProductSetImage'
        db.delete_table('productset_productsetimage')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'image.image': {
            'Meta': {'object_name': 'Image'},
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'product.variant': {
            'Meta': {'object_name': 'Variant'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sku': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'})
        },
        'productset.productset': {
            'Meta': {'object_name': 'ProductSet'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'productset.productsetimage': {
            'Meta': {'ordering': "['sort', 'id']", 'object_name': 'ProductSetImage', '_ormbases': ['image.Image']},
            'image_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['image.Image']", 'unique': 'True', 'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['productset.ProductSet']"}),
            'sort': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'productset.productsetitem': {
            'Meta': {'ordering': "['sort', 'id']", 'object_name': 'ProductSetItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'productset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['productset.ProductSet']"}),
            'sort': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Variant']"})
        }
    }

    complete_apps = ['productset']
