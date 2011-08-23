# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Edge'
        db.create_table('core_edge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('subject_id', self.gf('django.db.models.fields.IntegerField')()),
            ('object_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
            ('verb', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('core', ['Edge'])

        # Adding model 'Person'
        db.create_table('core_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['Person'])

        # Adding model 'Event'
        db.create_table('core_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['Event'])

        # Adding model 'Concept'
        db.create_table('core_concept', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['Concept'])

        # Adding model 'Object'
        db.create_table('core_object', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['Object'])


    def backwards(self, orm):
        
        # Deleting model 'Edge'
        db.delete_table('core_edge')

        # Deleting model 'Person'
        db.delete_table('core_person')

        # Deleting model 'Event'
        db.delete_table('core_event')

        # Deleting model 'Concept'
        db.delete_table('core_concept')

        # Deleting model 'Object'
        db.delete_table('core_object')


    models = {
        'core.concept': {
            'Meta': {'object_name': 'Concept'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.object': {
            'Meta': {'object_name': 'Object'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.person': {
            'Meta': {'object_name': 'Person'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['core']
