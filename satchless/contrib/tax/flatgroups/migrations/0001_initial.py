# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TaxGroup'
        db.create_table('flatgroups_taxgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('rate', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('rate_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('flatgroups', ['TaxGroup'])

        # Adding M2M table for field products on 'TaxGroup'
        db.create_table('flatgroups_taxgroup_products', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('taxgroup', models.ForeignKey(orm['flatgroups.taxgroup'], null=False)),
            ('product', models.ForeignKey(orm['product.product'], null=False))
        ))
        db.create_unique('flatgroups_taxgroup_products', ['taxgroup_id', 'product_id'])


    def backwards(self, orm):
        
        # Deleting model 'TaxGroup'
        db.delete_table('flatgroups_taxgroup')

        # Removing M2M table for field products on 'TaxGroup'
        db.delete_table('flatgroups_taxgroup_products')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'flatgroups.taxgroup': {
            'Meta': {'object_name': 'TaxGroup'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Product']", 'symmetrical': 'False'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'rate_name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'product.product': {
            'Meta': {'object_name': 'Product'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '80', 'db_index': 'True'})
        }
    }

    complete_apps = ['flatgroups']
