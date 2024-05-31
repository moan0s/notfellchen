from django.core.management import BaseCommand
from fellchensammlung.models import AdoptionNotice, Location


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
        adoption_notices_without_location = AdoptionNotice.objects.filter(location__isnull=True)
        num_of_all = AdoptionNotice.objects.count()
        num_without_location = adoption_notices_without_location.count()
        print(f"From {num_of_all} there are {num_without_location} adoption notices without location "
              f"({num_without_location/num_of_all*100:.2f}%)")
        for adoption_notice in adoption_notices_without_location:
            print(f"Searching {adoption_notice.location_string} in Nominatim")
            location = Location.get_location_from_string(adoption_notice.location_string)
            if location:
                adoption_notice.location = location
                adoption_notice.save()

        adoption_notices_without_location_new = AdoptionNotice.objects.filter(location__isnull=True)
        num_without_location_new = adoption_notices_without_location_new.count()
        num_new = num_without_location - num_without_location_new
        print(f"Added {num_new} new locations")
