from fellchensammlung.models import User, AdoptionNotice, AdoptionNoticeStatus


def gather_metrics_data():
    """USERS"""
    num_user = User.objects.count()
    num_staff = User.objects.filter(is_staff=True).count()

    """Adoption notices"""
    num_adoption_notices = AdoptionNotice.objects.count()
    adoption_notices_active = AdoptionNotice.objects.filter(
        adoptionnoticestatus__major_status=AdoptionNoticeStatus.ACTIVE)
    num_adoption_notices_active = adoption_notices_active.count()
    num_adoption_notices_closed = AdoptionNotice.objects.filter(
        adoptionnoticestatus__major_status=AdoptionNoticeStatus.CLOSED).count()
    num_adoption_notices_disabled = AdoptionNotice.objects.filter(
        adoptionnoticestatus__major_status=AdoptionNoticeStatus.DISABLED).count()
    num_adoption_notices_awaiting_action = AdoptionNotice.objects.filter(
        adoptionnoticestatus__major_status=AdoptionNoticeStatus.AWAITING_ACTION).count()

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
        'active_animals_per_sex': active_animals_per_sex
    }
    return data
