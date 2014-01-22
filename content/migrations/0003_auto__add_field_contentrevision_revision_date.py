# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ContentRevision.revision_date'
        db.add_column('content_contentrevision', 'revision_date',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 1, 22, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ContentRevision.revision_date'
        db.delete_column('content_contentrevision', 'revision_date')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['content']