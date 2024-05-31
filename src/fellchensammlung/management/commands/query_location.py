from django.core.management import BaseCommand
from fellchensammlung.tools.geo import GeoAPI


class Command(BaseCommand):
    help = 'Query location data to debug'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "query",
            help="The string to query",
        )

    def handle(self, *args, **options):
        geo_api = GeoAPI(debug=False)
        print(geo_api.get_location_from_string(options["query"]))
