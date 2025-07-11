from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core import mail
from fellchensammlung.models import User, Notification, TrustLevel, NotificationTypeChoices
from notfellchen.settings import base_url

NEWLINE = "\r\n"


def mail_admins_new_report(report):
    """
    Sends an e-mail to all users that should handle the report.
    """
    for moderator in User.objects.filter(trust_level__gt=TrustLevel.MODERATOR):
        report_url = base_url + report.get_absolute_url()
        context = {"report_url": report_url,
                   "user_comment": report.user_comment, }

        subject = _("Neue Meldung")
        html_message = render_to_string('fellchensammlung/mail/notifications/report.html', context)
        plain_message = strip_tags(html_message)

        mail.send_mail(subject,
                       plain_message,
                       from_email="info@notfellchen.org",
                       recipient_list=[moderator.email],
                       html_message=html_message)


def send_notification_email(notification_pk):
    notification = Notification.objects.get(pk=notification_pk)

    subject = f"{notification.title}"
    context = {"notification": notification, }
    if notification.notification_type == NotificationTypeChoices.NEW_REPORT_COMMENT or notification.notification_type == NotificationTypeChoices.NEW_REPORT_AN:
        context["user_comment"] = notification.report.user_comment
        context["report_url"] = f"{base_url}{notification.report.get_absolute_url()}"
        html_message = render_to_string('fellchensammlung/mail/notifications/report.html', context)
    elif notification.notification_type == NotificationTypeChoices.NEW_USER:
        html_message = render_to_string('fellchensammlung/mail/notifications/new-user.html', context)
    elif notification.notification_type == NotificationTypeChoices.AN_IS_TO_BE_CHECKED:
        html_message = render_to_string('fellchensammlung/mail/notifications/an-to-be-checked.html', context)
    elif notification.notification_type == NotificationTypeChoices.AN_WAS_DEACTIVATED:
        html_message = render_to_string('fellchensammlung/mail/notifications/an-deactivated.html', context)
    elif notification.notification_type == NotificationTypeChoices.AN_FOR_SEARCH_FOUND:
        html_message = render_to_string('fellchensammlung/mail/notifications/report.html', context)
    elif notification.notification_type == NotificationTypeChoices.NEW_COMMENT:
        html_message = render_to_string('fellchensammlung/mail/notifications/new-comment.html', context)
    else:
        raise NotImplementedError("Unknown notification type")

    plain_message = strip_tags(html_message)
    mail.send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL,
                   [notification.user_to_notify.email],
                   html_message=html_message)
