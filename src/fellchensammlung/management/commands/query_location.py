from django.core.management import BaseCommand
from fellchensammlung.models import Location


class Command(BaseCommand):
    help = 'Query location data to debug'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "query",
            help="The string to query",
        )

    def handle(self, *args, **options):
        print(Location.get_location_from_string(options["query"]))
