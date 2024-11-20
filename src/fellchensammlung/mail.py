from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core import mail
from fellchensammlung.models import User, CommentNotification, BaseNotification, TrustLevel
from notfellchen.settings import host

NEWLINE = "\r\n"


def mail_admins_new_report(report):
    subject = _("Neue Meldung")
    for moderator in User.objects.filter(trust_level__gt=TrustLevel.MODERATOR):
        greeting = _("Moin,") + "{NEWLINE}"
        new_report_text = _("es wurde ein Regelverstoß gemeldet.") + "{NEWLINE}"
        if len(report.reported_broken_rules.all()) > 0:
            reported_rules_text = (f"Ein Verstoß gegen die folgenden Regeln wurde gemeldet:{NEWLINE}"
                                   f"- {f'{NEWLINE} - '.join([str(r) for r in report.reported_broken_rules.all()])}{NEWLINE}")
        else:
            reported_rules_text = f"Es wurden keine Regeln angegeben gegen die Verstoßen wurde.{NEWLINE}"
        if report.user_comment:
            comment_text = f'Kommentar zum Report: "{report.user_comment}"{NEWLINE}'
        else:
            comment_text = f"Es wurde kein Kommentar hinzugefügt.{NEWLINE}"

        report_url = "https://" + host + report.get_absolute_url()
        link_text = f"Um alle Details zu sehen, geh bitte auf: {report_url}"
        body_text = greeting + new_report_text + reported_rules_text + comment_text + link_text
        message = mail.EmailMessage(subject, body_text, settings.DEFAULT_FROM_EMAIL, [moderator.email])
        message.send()


def send_notification_email(notification_pk):
    try:
        notification = CommentNotification.objects.get(pk=notification_pk)
    except CommentNotification.DoesNotExist:
        notification = BaseNotification.objects.get(pk=notification_pk)
    subject = f"🔔 {notification.title}"
    body_text = notification.text
    message = mail.EmailMessage(subject, body_text, settings.DEFAULT_FROM_EMAIL, [notification.user.email])
    message.send()
