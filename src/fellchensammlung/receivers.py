from django.db.models.signals import post_save
from django.dispatch import receiver
from fellchensammlung.models import BaseNotification, CommentNotification, User, TrustLevel
from .tasks import task_send_notification_email
from notfellchen.settings import host
from django.utils.translation import gettext_lazy as _


@receiver(post_save, sender=CommentNotification)
def comment_notification_receiver(sender, instance: BaseNotification, created: bool, **kwargs):
    base_notification_receiver(sender, instance, created, **kwargs)


@receiver(post_save, sender=BaseNotification)
def base_notification_receiver(sender, instance: BaseNotification, created: bool, **kwargs):
    if not created or not instance.user.email_notifications:
        return
    else:
        task_send_notification_email.delay(instance.pk)


@receiver(post_save, sender=User)
def notification_new_user(sender, instance: User, created: bool, **kwargs):
    NEWLINE = "\r\n"
    if not created:
        return
    # Create Notification text
    subject = _("Neuer User") + f": {instance.username}"
    new_user_text = _("Es hat sich eine neue Person registriert.") + f"{NEWLINE}"
    user_detail_text = _("Username") + f": {instance.username}{NEWLINE}" + _(
        "E-Mail") + f": {instance.email}{NEWLINE}"
    user_url = "https://" + host + instance.get_absolute_url()
    link_text = f"Um alle Details zu sehen, geh bitte auf: {user_url}"
    body_text = new_user_text + user_detail_text + link_text
    for moderator in User.objects.filter(trust_level__gt=TrustLevel.MODERATOR):
        notification = BaseNotification.objects.create(title=subject, text=body_text, user=moderator)
        notification.save()
