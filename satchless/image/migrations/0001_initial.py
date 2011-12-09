# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Image'
        db.create_table('image_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('image', ['Image'])

        # Adding model 'Thumbnail'
        db.create_table('image_thumbnail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('original', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['image.Image'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('size', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('image', ['Thumbnail'])

        # Adding unique constraint on 'Thumbnail', fields ['image', 'size']
        db.create_unique('image_thumbnail', ['image', 'size'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Thumbnail', fields ['image', 'size']
        db.delete_unique('image_thumbnail', ['image', 'size'])

        # Deleting model 'Image'
        db.delete_table('image_image')

        # Deleting model 'Thumbnail'
        db.delete_table('image_thumbnail')


    models = {
        'image.image': {
            'Meta': {'object_name': 'Image'},
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'image.thumbnail': {
            'Meta': {'unique_together': "(('image', 'size'),)", 'object_name': 'Thumbnail'},
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'original': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['image.Image']"}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['image']
