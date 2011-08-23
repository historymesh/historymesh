import json
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from core.models import Object, Person, Event, Concept, Edge

class Command(BaseCommand):
    help = """
    Imports the JSON exported by Weaver into the Antler database.
    """.strip()

    option_list = BaseCommand.option_list + (
        make_option(
            '-f', '--file',
            dest='file',
            action='store',
            help='Input file'
        ),
    )

    type_map = {
        "object": Object,
        "person": Person,
        "concept": Concept,
        "event": Event,
    }

    def handle(self, *app_labels, **options):
        input_file = options.get('file')

        if input_file is None:
            raise CommandError('Specify an input file')

        # Load the JSON
        with open(input_file) as fh:
            data = json.load(fh)

        # First pass: insert the things into the database
        relationships = []
        object_cache = {}
        for thing in data:
            # Get the class it maps to
            try:
                klass = self.type_map[thing['type']]
            except KeyError:
                print "Invalid thing (bad type): %r" % thing
                continue
            # Get the object if it exists
            instance = klass.objects.get_or_create(name=thing['name'])[0]
            # Delete all edges coming off of the object
            instance.outgoing().delete()
            # Store relationships for later use
            for verb, targets in thing['relationships'].items():
                for target in targets:
                    relationships.append((instance, target, verb))
            # Cache object
            object_cache[thing['name']] = instance
            print "Imported %s" % thing['name']
        
        # Second pass: create relationships
        print "Creating relationships..."
        for subject, object_name, verb in relationships:
            for verb, targets in thing['relationships'].items():
                edge = Edge(verb=verb)
                edge.subject = instance
                try:
                    edge.object = object_cache[object_name]
                except KeyError:
                    print "Relationship from %s to non-existent object %s" % (subject, object_name)
                    continue
                edge.save()
