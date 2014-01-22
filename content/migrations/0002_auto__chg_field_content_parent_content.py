# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Content.parent_content'
        db.alter_column('content_content', 'parent_content_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['content.Content']))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Content.parent_content'
        raise RuntimeError("Cannot reverse this migration. 'Content.parent_content' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Content.parent_content'
        db.alter_column('content_content', 'parent_content_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Content']))

    models = {
        'content.content': {
            'Meta': {'object_name': 'Content'},
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'application/octet-stream'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'parent_content': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'children'", 'null': 'True', 'blank': 'True', 'to': "orm['content.Content']"}),
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