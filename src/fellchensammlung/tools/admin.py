import logging

from random import randint

from fellchensammlung.tools.model_helpers import AdoptionNoticeStatusChoices
from notfellchen import settings
from django.utils import timezone
from datetime import timedelta

from django_super_deduper.merge import MergedModelInstance
from django.template.loader import render_to_string
from django.core import mail
from django.utils.html import strip_tags

from fellchensammlung.models import AdoptionNotice, Location, RescueOrganization, Log, \
    Notification, NotificationTypeChoices
from fellchensammlung.tools.misc import is_404


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
    n_weeks_ago = now - timedelta(weeks=weeks)

    # Query for active adoption notices that were not checked in the last n weeks
    unchecked_adoptions = AdoptionNotice.objects.filter(
        last_checked__lte=n_weeks_ago
    )
    active_unchecked_adoptions = [adoption for adoption in unchecked_adoptions if adoption.is_active]
    return active_unchecked_adoptions


def get_active_adoption_notices():
    ans = AdoptionNotice.objects.all()
    active_adoptions = [adoption for adoption in ans if adoption.is_active]
    return active_adoptions


def deactivate_unchecked_adoption_notices():
    for adoption_notice in get_unchecked_adoption_notices(weeks=3):
        adoption_notice.set_unchecked()


def deactivate_404_adoption_notices():
    for adoption_notice in get_active_adoption_notices():
        if adoption_notice.further_information and adoption_notice.further_information != "":
            if is_404(adoption_notice.further_information):
                adoption_notice.adoption_notice_status = AdoptionNoticeStatusChoices.Closed.LINK_TO_MORE_INFO_NOT_REACHABLE
                adoption_notice.save()
                logging_msg = f"Automatically set Adoption Notice {adoption_notice.id} closed as link to more information returened 404"
                logging.info(logging_msg)
                Log.objects.create(action="automated", text=logging_msg)

                deactivation_message = f'Die Vermittlung  [{adoption_notice.name}]({adoption_notice.get_absolute_url()}) wurde automatisch deaktiviert, da die Website unter "Mehr Informationen" nicht mehr online ist.'
                for subscription in adoption_notice.get_subscriptions():
                    Notification.objects.create(user_to_notify=subscription.owner,
                                                notification_type=NotificationTypeChoices.AN_WAS_DEACTIVATED,
                                                title="Vermittlung deaktiviert",
                                                adoption_notice=adoption_notice,
                                                text=deactivation_message)


def dedup_location(location: Location, destructive=False):
    duplicates = Location.objects.filter(place_id=location.place_id).exclude(id=location.id)
    merged_object = MergedModelInstance.create(location, duplicates)
    if destructive:
        duplicates.delete()
        print("Deleted duplicate locations")
    return merged_object


def dedup_locations():
    location_ids = list(Location.objects.values_list("id", flat=True))
    for location_id in location_ids:
        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            # Already deleted as a duplicate
            continue
        dedup_location(location, destructive=True)


def export_orgs_as_vcf():
    rescue_orgs = RescueOrganization.objects.filter(phone_number__isnull=False)
    result = render_to_string(template_name="fellchensammlung/contacts.vcf",
                              context={"contacts": rescue_orgs,
                                       "current_time": timezone.now(),
                                       "categories": "Tierheim"})
    filename = "contacts.vcf"
    with open(filename, "w") as f:
        f.write(result)
    print(f"Wrote {len(rescue_orgs)} contacts to {filename}")


def send_test_email(email):
    subject = 'Test E-Mail'
    html_message = render_to_string('fellchensammlung/mail/test.html', {'context': 'values'})
    plain_message = strip_tags(html_message)
    from_email = f'From <{settings.DEFAULT_FROM_EMAIL}>'
    to = email

    mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)


def mask_organization_contact_data(catchall_domain="example.org"):
    """
    Masks e-mails, so they are all sent to one domain, preferably a catchall domain.
    """
    rescue_orgs_with_phone_number = RescueOrganization.objects.filter(phone_number__isnull=False)
    for rescue_org_with_phone_number in rescue_orgs_with_phone_number:
        rescue_org_with_phone_number.phone_number = randint(100000000000, 1000000000000)
        rescue_org_with_phone_number.save()
    rescue_orgs_with_email = RescueOrganization.objects.filter(email__isnull=False)
    for rescue_org_with_email in rescue_orgs_with_email:
        rescue_org_with_email.email = f"{rescue_org_with_email.email.replace('@', '-')}@{catchall_domain}"
        rescue_org_with_email.save()

