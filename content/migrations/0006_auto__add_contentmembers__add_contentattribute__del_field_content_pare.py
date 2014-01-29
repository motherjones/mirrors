# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ContentMembers'
        db.create_table('content_contentmembers', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['content.Content'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Content'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('content', ['ContentMembers'])

        # Adding model 'ContentAttribute'
        db.create_table('content_contentattribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attributes', to=orm['content.Content'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Content'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('content', ['ContentAttribute'])

        # Deleting field 'Content.parent_content'
        db.delete_column('content_content', 'parent_content_id')


    def backwards(self, orm):
        # Deleting model 'ContentMembers'
        db.delete_table('content_contentmembers')

        # Deleting model 'ContentAttribute'
        db.delete_table('content_contentattribute')

        # Adding field 'Content.parent_content'
        db.add_column('content_content', 'parent_content',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='members', null=True, to=orm['content.Content'], blank=True),
                      keep_default=False)


    models = {
        'content.content': {
            'Meta': {'object_name': 'Content'},
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'schema': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'content.contentattribute': {
            'Meta': {'object_name': 'ContentAttribute'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.Content']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attributes'", 'to': "orm['content.Content']"})
        },
        'content.contentmembers': {
            'Meta': {'object_name': 'ContentMembers'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.Content']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['content.Content']"})
        },
        'content.contentrevision': {
            'Meta': {'object_name': 'ContentRevision'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': "orm['content.Content']"}),
            'data': ('django.db.models.fields.BinaryField', [], {}),
            'diff': ('django.db.models.fields.BinaryField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'revision_number': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['content']