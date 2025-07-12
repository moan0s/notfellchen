from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core import mail
from fellchensammlung.models import User, Notification, TrustLevel, NotificationTypeChoices
from fellchensammlung.tools.model_helpers import ndm


def notify_mods_new_report(report, notification_type):
    """
    Sends an e-mail to all users that should handle the report.
    """
    for moderator in User.objects.filter(trust_level__gt=TrustLevel.MODERATOR):
        if notification_type == NotificationTypeChoices.NEW_REPORT_AN:
            title = _("Vermittlung gemeldet")
        elif notification_type == NotificationTypeChoices.NEW_COMMENT:
            title = _("Kommentar gemeldet")
        else:
            raise NotImplementedError
        notification = Notification.objects.create(
            notification_type=notification_type,
            user_to_notify=moderator,
            report=report,
            title=title,
        )
        notification.save()


def send_notification_email(notification_pk):
    notification = Notification.objects.get(pk=notification_pk)

    subject = f"{notification.title}"
    context = {"notification": notification, }
    html_message = render_to_string(ndm[notification.notification_type].email_html_template, context)
    plain_message = render_to_string(ndm[notification.notification_type].email_plain_template, context)

    mail.send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL,
                   [notification.user_to_notify.email],
                   html_message=html_message)
