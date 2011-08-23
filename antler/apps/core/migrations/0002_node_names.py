# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Event.name'
        db.add_column('core_event', 'name', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=1024), keep_default=False)

        # Adding field 'Concept.name'
        db.add_column('core_concept', 'name', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=1024), keep_default=False)

        # Adding field 'Object.name'
        db.add_column('core_object', 'name', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=1024), keep_default=False)

        # Adding field 'Person.name'
        db.add_column('core_person', 'name', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=1024), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Event.name'
        db.delete_column('core_event', 'name')

        # Deleting field 'Concept.name'
        db.delete_column('core_concept', 'name')

        # Deleting field 'Object.name'
        db.delete_column('core_object', 'name')

        # Deleting field 'Person.name'
        db.delete_column('core_person', 'name')


    models = {
        'core.concept': {
            'Meta': {'object_name': 'Concept'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'})
        },
        'core.edge': {
            'Meta': {'object_name': 'Edge'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'object_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subject_id': ('django.db.models.fields.IntegerField', [], {}),
            'subject_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.event': {
            'Meta': {'object_name': 'Event'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'})
        },
        'core.object': {
            'Meta': {'object_name': 'Object'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'})
        },
        'core.person': {
            'Meta': {'object_name': 'Person'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'})
        }
    }

    complete_apps = ['core']
