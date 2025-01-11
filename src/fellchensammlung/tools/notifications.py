from fellchensammlung.models import User, AdoptionNoticeNotification, TrustLevel


def notify_moderators_of_AN_to_be_checked(adoption_notice):
    if adoption_notice.is_disabled_unchecked:
        for moderator in User.objects.filter(trust_level__gt=TrustLevel.MODERATOR):
            AdoptionNoticeNotification.objects.create(adoption_notice=adoption_notice,
                                                      user=moderator,
                                                      title=f" Prüfe Vermittlung {adoption_notice}",
                                                      text=f"{adoption_notice} muss geprüft werden bevor sie veröffentlicht wird.",
                                                      )