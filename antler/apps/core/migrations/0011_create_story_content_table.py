# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'StoryContent'
        db.create_table('core_storycontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=1024)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('timeline_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('display_date', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('core', ['StoryContent'])


    def backwards(self, orm):
        
        # Deleting model 'StoryContent'
        db.delete_table('core_storycontent')


    models = {
        'core.concept': {
            'Meta': {'object_name': 'Concept'},
            'display_date': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timeline_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.edge': {
            'Meta': {'unique_together': "[('subject_type', 'subject_id', 'object_type', 'object_id', 'verb', 'story')]", 'object_name': 'Edge'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'object_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'edges'", 'null': 'True', 'to': "orm['core.Story']"}),
            'subject_id': ('django.db.models.fields.IntegerField', [], {}),
            'subject_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.event': {
            'Meta': {'object_name': 'Event'},
            'display_date': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timeline_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.object': {
            'Meta': {'object_name': 'Object'},
            'display_date': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timeline_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.person': {
            'Meta': {'object_name': 'Person'},
            'display_date': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timeline_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.story': {
            'Meta': {'object_name': 'Story'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'core.storycontent': {
            'Meta': {'object_name': 'StoryContent'},
            'display_date': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timeline_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['core']
