from django.core.management import BaseCommand
from fellchensammlung.models import AdoptionNotice, Location
from fellchensammlung.tools.geo import clean_locations


class Command(BaseCommand):
    help = 'Clean up empty locations by re-querying them'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--all",
            action="store_true",
            help="Re-query all locations, not only where they are empty",
        )

    def handle(self, *args, **options):
        clean_locations(quiet=False)