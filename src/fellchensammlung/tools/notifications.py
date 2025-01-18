from fellchensammlung.models import User, AdoptionNoticeNotification, TrustLevel


def notify_of_AN_to_be_checked(adoption_notice):
    if adoption_notice.is_disabled_unchecked:
        users_to_notify = set(User.objects.filter(trust_level__gt=TrustLevel.MODERATOR))
        users_to_notify.add(adoption_notice.owner)
        for user in users_to_notify:
            AdoptionNoticeNotification.objects.create(adoption_notice=adoption_notice,
                                                      user=user,
                                                      title=f" Prüfe Vermittlung {adoption_notice}",
                                                      text=f"{adoption_notice} muss geprüft werden bevor sie veröffentlicht wird.",
                                                      )