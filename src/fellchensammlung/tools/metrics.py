from fellchensammlung.models import User, AdoptionNotice, AdoptionNoticeStatus


def gather_metrics_data():
    """USERS"""
    num_user = User.objects.count()
    num_staff = User.objects.filter(is_staff=True).count()

    """Adoption notices"""
    num_adoption_notices = AdoptionNotice.objects.count()
    num_adoption_notices_active = AdoptionNotice.objects.filter(adoptionnoticestatus__major_status=AdoptionNoticeStatus.ACTIVE).count()

    adoption_notices_without_location = AdoptionNotice.objects.filter(location__isnull=True).count()
    data = {
        'users': num_user,
        'staff': num_staff,

        'adoption_notices': num_adoption_notices,
        'adoption_notices_active': num_adoption_notices_active,
        'adoption_notices_without_location': adoption_notices_without_location
    }
    return data
