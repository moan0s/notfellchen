from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core import mail
from fellchensammlung.models import User, CommentNotification, BaseNotification, TrustLevel
from notfellchen.settings import host

NEWLINE = "\r\n"


def mail_admins_new_report(report):
    """
    Sends an e-mail to all users that should handle the report.
    """
    for moderator in User.objects.filter(trust_level__gt=TrustLevel.MODERATOR):
        report_url = "https://" + host + report.get_absolute_url()
        context = {"report_url": report_url,
                   "user_comment": report.user_comment,}

        subject = _("Neue Meldung")
        html_message = render_to_string('fellchensammlung/mail/report.html', context)
        plain_message = strip_tags(html_message)

        mail.send_mail(subject,
                       plain_message,
                       from_email="info@notfellchen.org",
                       recipient_list=[moderator.email],
                       html_message=html_message)


def send_notification_email(notification_pk):
    try:
        notification = CommentNotification.objects.get(pk=notification_pk)
    except CommentNotification.DoesNotExist:
        notification = BaseNotification.objects.get(pk=notification_pk)
    subject = f"🔔 {notification.title}"
    body_text = notification.text
    message = mail.EmailMessage(subject, body_text, settings.DEFAULT_FROM_EMAIL, [notification.user.email])
    message.send()
