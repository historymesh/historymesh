# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Event.timeline_date'
        db.add_column('core_event', 'timeline_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Event.display_date'
        db.add_column('core_event', 'display_date', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Adding field 'Person.timeline_date'
        db.add_column('core_person', 'timeline_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Person.display_date'
        db.add_column('core_person', 'display_date', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Adding field 'Object.timeline_date'
        db.add_column('core_object', 'timeline_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Object.display_date'
        db.add_column('core_object', 'display_date', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Adding field 'Concept.timeline_date'
        db.add_column('core_concept', 'timeline_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Concept.display_date'
        db.add_column('core_concept', 'display_date', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Event.timeline_date'
        db.delete_column('core_event', 'timeline_date')

        # Deleting field 'Event.display_date'
        db.delete_column('core_event', 'display_date')

        # Deleting field 'Person.timeline_date'
        db.delete_column('core_person', 'timeline_date')

        # Deleting field 'Person.display_date'
        db.delete_column('core_person', 'display_date')

        # Deleting field 'Object.timeline_date'
        db.delete_column('core_object', 'timeline_date')

        # Deleting field 'Object.display_date'
        db.delete_column('core_object', 'display_date')

        # Deleting field 'Concept.timeline_date'
        db.delete_column('core_concept', 'timeline_date')

        # Deleting field 'Concept.display_date'
        db.delete_column('core_concept', 'display_date')


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
            'Meta': {'object_name': 'Edge'},
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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['core']
