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

    def handle(self, *app_labels, **options):
        input_file = options.get('file')

        if input_file is None:
            raise CommandError('Specify an input file')

        # Load the JSON
        with open(input_file) as fh:
            data = json.load(fh)

        # Import it
        import_from_json(data, clean=True, verbose=True)
