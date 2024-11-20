from django.db.models.signals import post_save
from django.dispatch import receiver
from fellchensammlung.models import BaseNotification, CommentNotification
from .tasks import task_send_notification_email


@receiver(post_save, sender=CommentNotification)
def comment_notification_receiver(sender, instance: BaseNotification, created: bool, **kwargs):
    base_notification_receiver(sender, instance, created, **kwargs)


@receiver(post_save, sender=BaseNotification)
def base_notification_receiver(sender, instance: BaseNotification, created: bool, **kwargs):
    if not created or not instance.user.email_notifications:
        return
    else:
        task_send_notification_email.delay(instance.pk)
