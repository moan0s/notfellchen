from datetime import timedelta

from django.utils import timezone

from fellchensammlung.models import User, AdoptionNotice, AdoptionNoticeStatusChoices, Animal, RescueOrganization


def get_rescue_org_check_stats():
    timeframe = timezone.now().date() - timedelta(days=14)
    num_rescue_orgs_to_check = RescueOrganization.objects.filter(exclude_from_check=False).filter(
        last_checked__lt=timeframe).count()
    num_rescue_orgs_checked = RescueOrganization.objects.filter(exclude_from_check=False).filter(
        last_checked__gte=timeframe).count()

    try:
        percentage_checked = 100 * num_rescue_orgs_checked / (num_rescue_orgs_to_check + num_rescue_orgs_checked)
    except ZeroDivisionError:
        percentage_checked = 100
    return num_rescue_orgs_to_check, num_rescue_orgs_checked, percentage_checked


def gather_metrics_data():
    """USERS"""
    num_user = User.objects.count()
    num_staff = User.objects.filter(is_staff=True).count()

    """Adoption notices"""
    num_adoption_notices = AdoptionNotice.objects.count()
    adoption_notices_active = AdoptionNotice.objects.filter(
        adoption_notice_status__in=AdoptionNoticeStatusChoices.Active.values)
    num_adoption_notices_active = adoption_notices_active.count()
    num_adoption_notices_closed = AdoptionNotice.objects.filter(
        adoption_notice_status__in=AdoptionNoticeStatusChoices.Closed.values).count()
    num_adoption_notices_disabled = AdoptionNotice.objects.filter(
        adoption_notice_status__in=AdoptionNoticeStatusChoices.Disabled.values).count()
    num_adoption_notices_awaiting_action = AdoptionNotice.objects.filter(
        adoption_notice_status__in=AdoptionNoticeStatusChoices.AwaitingAction.values).count()

    adoption_notices_without_location = AdoptionNotice.objects.filter(location__isnull=True).count()

    active_animals = 0
    active_animals_per_sex = {}
    for adoption_notice in adoption_notices_active:
        nps = adoption_notice.num_per_sex
        for sex in nps:
            number_of_animals = nps[sex]
            try:
                active_animals_per_sex[sex] += number_of_animals
            except KeyError:
                active_animals_per_sex[sex] = number_of_animals
            active_animals += number_of_animals

    num_animal_shelters = RescueOrganization.objects.all().count()

    num_rescue_orgs_to_check, num_rescue_orgs_checked, percentage_checked = get_rescue_org_check_stats()

    data = {
        'users': num_user,
        'staff': num_staff,

        'adoption_notices': num_adoption_notices,
        'adoption_notices_by_status': {
            'active': num_adoption_notices_active,
            'closed': num_adoption_notices_closed,
            'disabled': num_adoption_notices_disabled,
            'awaiting_action': num_adoption_notices_awaiting_action,
        },
        'adoption_notices_without_location': adoption_notices_without_location,
        'active_animals': active_animals,
        'active_animals_per_sex': active_animals_per_sex,
        'rescue_organizations': num_animal_shelters,
        'rescue_organization_check': {
            'rescue_orgs_to_check': num_rescue_orgs_to_check,
            'rescue_orgs_checked': num_rescue_orgs_checked,
            'percentage_checked': percentage_checked,
        }
    }
    return data
