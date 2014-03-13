# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'ContentRevision'
        db.delete_table('mirrors_contentrevision')

        # Deleting model 'ContentAttribute'
        db.delete_table('mirrors_contentattribute')

        # Deleting model 'Content'
        db.delete_table('mirrors_content')

        # Deleting model 'ContentMember'
        db.delete_table('mirrors_contentmember')

        # Adding model 'Component'
        db.create_table('mirrors_component', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(default={})),
            ('content_type', self.gf('django.db.models.fields.CharField')(default='none', max_length=50)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('schema_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('mirrors', ['Component'])

        # Adding model 'ComponentAttribute'
        db.create_table('mirrors_componentattribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attributes', to=orm['mirrors.Component'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirrors.Component'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('added_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('mirrors', ['ComponentAttribute'])

        # Adding model 'ComponentRevision'
        db.create_table('mirrors_componentrevision', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('django.db.models.fields.BinaryField')()),
            ('diff', self.gf('django.db.models.fields.BinaryField')(null=True, blank=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(default={})),
            ('revision_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('revision_number', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('component', self.gf('django.db.models.fields.related.ForeignKey')(related_name='revisions', to=orm['mirrors.Component'])),
        ))
        db.send_create_signal('mirrors', ['ComponentRevision'])

        # Adding model 'ComponentMember'
        db.create_table('mirrors_componentmember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['mirrors.Component'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirrors.Component'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mirrors', ['ComponentMember'])


    def backwards(self, orm):
        # Adding model 'ContentRevision'
        db.create_table('mirrors_contentrevision', (
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='revisions', to=orm['mirrors.Content'])),
            ('revision_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('revision_number', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('diff', self.gf('django.db.models.fields.BinaryField')(null=True, blank=True)),
            ('data', self.gf('django.db.models.fields.BinaryField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(default={})),
        ))
        db.send_create_signal('mirrors', ['ContentRevision'])

        # Adding model 'ContentAttribute'
        db.create_table('mirrors_contentattribute', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attributes', to=orm['mirrors.Content'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirrors.Content'])),
            ('added_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('mirrors', ['ContentAttribute'])

        # Adding model 'Content'
        db.create_table('mirrors_content', (
            ('content_type', self.gf('django.db.models.fields.CharField')(default='none', max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, unique=True)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('schema_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(default={})),
        ))
        db.send_create_signal('mirrors', ['Content'])

        # Adding model 'ContentMember'
        db.create_table('mirrors_contentmember', (
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['mirrors.Content'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirrors.Content'])),
        ))
        db.send_create_signal('mirrors', ['ContentMember'])

        # Deleting model 'Component'
        db.delete_table('mirrors_component')

        # Deleting model 'ComponentAttribute'
        db.delete_table('mirrors_componentattribute')

        # Deleting model 'ComponentRevision'
        db.delete_table('mirrors_componentrevision')

        # Deleting model 'ComponentMember'
        db.delete_table('mirrors_componentmember')


    models = {
        'mirrors.component': {
            'Meta': {'object_name': 'Component'},
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'schema_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'mirrors.componentattribute': {
            'Meta': {'object_name': 'ComponentAttribute'},
            'added_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirrors.Component']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attributes'", 'to': "orm['mirrors.Component']"})
        },
        'mirrors.componentmember': {
            'Meta': {'object_name': 'ComponentMember'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mirrors.Component']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['mirrors.Component']"})
        },
        'mirrors.componentrevision': {
            'Meta': {'object_name': 'ComponentRevision'},
            'component': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': "orm['mirrors.Component']"}),
            'data': ('django.db.models.fields.BinaryField', [], {}),
            'diff': ('django.db.models.fields.BinaryField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'revision_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'revision_number': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['mirrors']