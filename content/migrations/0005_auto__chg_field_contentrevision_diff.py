# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ContentRevision.diff'
        db.alter_column('content_contentrevision', 'diff', self.gf('django.db.models.fields.BinaryField')(null=True))

    def backwards(self, orm):

        # Changing field 'ContentRevision.diff'
        db.alter_column('content_contentrevision', 'diff', self.gf('django.db.models.fields.BinaryField')(default=None))

    models = {
        'content.content': {
            'Meta': {'object_name': 'Content'},
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'parent_content': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'members'", 'null': 'True', 'blank': 'True', 'to': "orm['content.Content']"}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'schema': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
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