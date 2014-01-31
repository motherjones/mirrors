# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ContentAttribute.added_time'
        db.add_column('mirrors_contentattribute', 'added_time',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 1, 30, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ContentAttribute.added_time'
        db.delete_column('mirrors_contentattribute', 'added_time')


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
            'added_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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