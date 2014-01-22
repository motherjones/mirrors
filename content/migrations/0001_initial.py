# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Content'
        db.create_table('content_content', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(default={})),
            ('content_type', self.gf('django.db.models.fields.CharField')(default='application/octet-stream', max_length=50)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('schema', self.gf('jsonfield.fields.JSONField')(default={})),
            ('parent_content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', to=orm['content.Content'])),
        ))
        db.send_create_signal('content', ['Content'])

        # Adding model 'ContentRevision'
        db.create_table('content_contentrevision', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('django.db.models.fields.BinaryField')()),
            ('diff', self.gf('django.db.models.fields.BinaryField')()),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='revisions', to=orm['content.Content'])),
        ))
        db.send_create_signal('content', ['ContentRevision'])


    def backwards(self, orm):
        # Deleting model 'Content'
        db.delete_table('content_content')

        # Deleting model 'ContentRevision'
        db.delete_table('content_contentrevision')


    models = {
        'content.content': {
            'Meta': {'object_name': 'Content'},
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'application/octet-stream'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'parent_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'to': "orm['content.Content']"}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'schema': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'content.contentrevision': {
            'Meta': {'object_name': 'ContentRevision'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': "orm['content.Content']"}),
            'data': ('django.db.models.fields.BinaryField', [], {}),
            'diff': ('django.db.models.fields.BinaryField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['content']