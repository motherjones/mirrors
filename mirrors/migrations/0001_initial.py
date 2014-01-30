# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Content'
        db.create_table('mirrors_content', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(default={})),
            ('content_type', self.gf('django.db.models.fields.CharField')(default='none', max_length=50)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('schema_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('mirrors', ['Content'])

        # Adding model 'ContentAttribute'
        db.create_table('mirrors_contentattribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attributes', to=orm['mirrors.Content'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirrors.Content'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('mirrors', ['ContentAttribute'])

        # Adding model 'ContentMembers'
        db.create_table('mirrors_contentmembers', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['mirrors.Content'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirrors.Content'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mirrors', ['ContentMembers'])

        # Adding model 'ContentRevision'
        db.create_table('mirrors_contentrevision', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('django.db.models.fields.BinaryField')()),
            ('diff', self.gf('django.db.models.fields.BinaryField')(null=True, blank=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(default={})),
            ('revision_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('revision_number', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='revisions', to=orm['mirrors.Content'])),
        ))
        db.send_create_signal('mirrors', ['ContentRevision'])


    def backwards(self, orm):
        # Deleting model 'Content'
        db.delete_table('mirrors_content')

        # Deleting model 'ContentAttribute'
        db.delete_table('mirrors_contentattribute')

        # Deleting model 'ContentMembers'
        db.delete_table('mirrors_contentmembers')

        # Deleting model 'ContentRevision'
        db.delete_table('mirrors_contentrevision')


    models = {
        'mirrors.content': {
            'Meta': {'object_name': 'Content'},
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'schema_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'mirrors.contentattribute': {
            'Meta': {'object_name': 'ContentAttribute'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirrors.Content']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attributes'", 'to': "orm['mirrors.Content']"})
        },
        'mirrors.contentmembers': {
            'Meta': {'object_name': 'ContentMembers'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirrors.Content']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['mirrors.Content']"})
        },
        'mirrors.contentrevision': {
            'Meta': {'object_name': 'ContentRevision'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': "orm['mirrors.Content']"}),
            'data': ('django.db.models.fields.BinaryField', [], {}),
            'diff': ('django.db.models.fields.BinaryField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'revision_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'revision_number': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['mirrors']