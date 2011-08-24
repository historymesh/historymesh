# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Event.date_fuzziness'
        db.delete_column('core_event', 'date_fuzziness')

        # Deleting field 'Event.date'
        db.delete_column('core_event', 'date')

        # Deleting field 'Person.birth_date'
        db.delete_column('core_person', 'birth_date')

        # Deleting field 'Person.death_date'
        db.delete_column('core_person', 'death_date')

        # Deleting field 'Person.death_date_fuzziness'
        db.delete_column('core_person', 'death_date_fuzziness')

        # Deleting field 'Person.birth_date_fuzziness'
        db.delete_column('core_person', 'birth_date_fuzziness')


    def backwards(self, orm):
        
        # Adding field 'Event.date_fuzziness'
        db.add_column('core_event', 'date_fuzziness', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Event.date'
        db.add_column('core_event', 'date', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Person.birth_date'
        db.add_column('core_person', 'birth_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Person.death_date'
        db.add_column('core_person', 'death_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Person.death_date_fuzziness'
        db.add_column('core_person', 'death_date_fuzziness', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'Person.birth_date_fuzziness'
        db.add_column('core_person', 'birth_date_fuzziness', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)


    models = {
        'core.concept': {
            'Meta': {'object_name': 'Concept'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'core.object': {
            'Meta': {'object_name': 'Object'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'core.person': {
            'Meta': {'object_name': 'Person'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'core.story': {
            'Meta': {'object_name': 'Story'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['core']
