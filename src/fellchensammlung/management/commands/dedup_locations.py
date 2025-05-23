from django.core.management import BaseCommand
from fellchensammlung.tools.admin import dedup_locations


class Command(BaseCommand):
    help = 'Deduplicate locations based on place_id'

    def handle(self, *args, **options):
        dedup_locations()

