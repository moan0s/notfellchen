from django.utils import timezone
from datetime import timedelta

from fellchensammlung.models import AdoptionNotice, Location, RescueOrganization, AdoptionNoticeStatus


def clean_locations(quiet=True):
    # ADOPTION NOTICES
    adoption_notices_without_location = AdoptionNotice.objects.filter(location__isnull=True)
    num_of_all = AdoptionNotice.objects.count()
    num_without_location = adoption_notices_without_location.count()
    if not quiet:
        print(f"From {num_of_all} there are {num_without_location} adoption notices without location "
              f"({num_without_location / num_of_all * 100:.2f}%)")
    for adoption_notice in adoption_notices_without_location:
        if not quiet:
            print(f"Searching {adoption_notice.location_string} in Nominatim")
        location = Location.get_location_from_string(adoption_notice.location_string)
        if location:
            adoption_notice.location = location
            adoption_notice.save()

    adoption_notices_without_location_new = AdoptionNotice.objects.filter(location__isnull=True)
    num_without_location_new = adoption_notices_without_location_new.count()
    num_new = num_without_location - num_without_location_new
    if not quiet:
        print(f"Added {num_new} new locations")

    # RESCUE ORGANIZATIONS
    rescue_orgs_without_location = RescueOrganization.objects.filter(location__isnull=True)
    num_of_all = RescueOrganization.objects.count()
    num_without_location = rescue_orgs_without_location.count()
    if not quiet:
        print(f"From {num_of_all} there are {num_without_location} adoption notices without location "
              f"({num_without_location / num_of_all * 100:.2f}%)")
    for rescue_org in rescue_orgs_without_location:
        if not quiet:
            print(f"Searching {rescue_org.location_string} in Nominatim")
        location = Location.get_location_from_string(rescue_org.location_string)
        if location:
            rescue_org.location = location
            rescue_org.save()

    rescue_orgs_without_location_new = RescueOrganization.objects.filter(location__isnull=True)
    num_without_location_new = rescue_orgs_without_location_new.count()
    num_new = num_without_location - num_without_location_new
    if not quiet:
        print(f"Added {num_new} new locations")


def get_unchecked_adoption_notices(weeks=3):
    now = timezone.now()
    three_weeks_ago = now - timedelta(weeks=weeks)

    # Query for active adoption notices that were checked in the last three weeks
    unchecked_adoptions = AdoptionNotice.objects.filter(
        last_checked__gte=three_weeks_ago
    )
    active_unchecked_adoptions = [adoption for adoption in unchecked_adoptions if adoption.is_active]
    return active_unchecked_adoptions


def deactivate_unchecked_adoption_notices():
    for adoption_notice in get_unchecked_adoption_notices(weeks=3):
        AdoptionNoticeStatus.objects.get(adoption_notice=adoption_notice).deactivate_unchecked()
