from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

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

        #TODO: Load the file and do some stuff with it
        print input_file

