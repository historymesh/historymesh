import json
from django.core.management.base import BaseCommand, CommandError
from core.models import Object, Person, Event, Concept, Edge
from search.utils import collection, index, set_schema

class Command(BaseCommand):
    help = """
    Rebuilds the search engine index.
    """.strip()

    def handle(self, *app_labels, **options):
        collection.delete()
        set_schema()
	for obj in Object.objects.all():
	    index(obj)
	for obj in Person.objects.all():
	    index(obj)
	for obj in Event.objects.all():
	    index(obj)
	for obj in Concept.objects.all():
	    index(obj)
        checkpoint = collection.checkpoint().wait()
        if checkpoint.total_errors != 0:
            print "Errors while indexing: %s" % checkpoint.errors
        else:
            print "Indexing complete"
