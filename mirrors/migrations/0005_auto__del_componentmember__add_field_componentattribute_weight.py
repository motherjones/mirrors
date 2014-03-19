# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'ComponentMember'
        db.delete_table('mirrors_componentmember')

        # Adding field 'ComponentAttribute.weight'
        db.add_column('mirrors_componentattribute', 'weight',
                      self.gf('django.db.models.fields.IntegerField')(default=9999),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'ComponentMember'
        db.create_table('mirrors_componentmember', (
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['mirrors.Component'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mirrors.Component'])),
        ))
        db.send_create_signal('mirrors', ['ComponentMember'])

        # Deleting field 'ComponentAttribute.weight'
        db.delete_column('mirrors_componentattribute', 'weight')


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
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attributes'", 'to': "orm['mirrors.Component']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
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