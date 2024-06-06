from fellchensammlung.models import User, AdoptionNotice, AdoptionNoticeStatus


def gather_metrics_data():
    """USERS"""
    num_user = User.objects.count()
    num_staff = User.objects.filter(is_staff=True).count()

    """Adoption notices"""
    num_adoption_notices = AdoptionNotice.objects.count()
    num_adoption_notices_active = AdoptionNotice.objects.filter(
        adoptionnoticestatus__major_status=AdoptionNoticeStatus.ACTIVE).count()
    num_adoption_notices_closed = AdoptionNotice.objects.filter(
        adoptionnoticestatus__major_status=AdoptionNoticeStatus.CLOSED).count()
    num_adoption_notices_disabled = AdoptionNotice.objects.filter(
        adoptionnoticestatus__major_status=AdoptionNoticeStatus.DISABLED).count()
    num_adoption_notices_in_review = AdoptionNotice.objects.filter(
        adoptionnoticestatus__major_status=AdoptionNoticeStatus.IN_REVIEW).count()

    adoption_notices_without_location = AdoptionNotice.objects.filter(location__isnull=True).count()
    data = {
        'users': num_user,
        'staff': num_staff,

        'adoption_notices': num_adoption_notices,
        'adoption_notices_by_status': {
            'active': num_adoption_notices_active,
            'closed': num_adoption_notices_closed,
            'disabled': num_adoption_notices_disabled,
            'in_review': num_adoption_notices_in_review,
        },
        'adoption_notices_without_location': adoption_notices_without_location
    }
    return data
