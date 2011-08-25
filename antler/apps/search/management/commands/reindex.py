import json
from django.core.management.base import BaseCommand, CommandError
from core.models import Object, Person, Event, Concept, Edge
from search.search import index

class Command(BaseCommand):
    help = """
    Rebuilds the search engine index.
    """.strip()

    def handle(self, *app_labels, **options):
	for obj in Object.objects.all():
	    index(obj)
	for obj in Person.objects.all():
	    index(obj)
	for obj in Event.objects.all():
	    index(obj)
	for obj in Concept.objects.all():
	    index(obj)
