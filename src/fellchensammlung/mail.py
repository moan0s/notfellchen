import django.conf.global_settings

from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.conf import settings
from django.core import mail
from django.db.models import Q, Min
from fellchensammlung.models import User
from notfellchen.settings import host


def mail_admins_new_report(report):
    subject = _("Neue Meldung")
    for moderator in User.objects.filter(trust_level__gt=User.TRUST_LEVEL[User.MODERATOR]):
        greeting = _("Moin,") + "\r\n"
        new_report_text = _("es wurde ein Regelverstoß gemeldet.") + "\r\n"
        if len(report.reported_broken_rules.all()) > 0:
            reported_rules_text = (f"Ein Verstoß gegen die folgenden Regeln wurde gemeldet:\r\n"
                                   f"- {'\r\n - '.join([str(r) for r in report.reported_broken_rules.all()])}\r\n")
        else:
            reported_rules_text = f"Es wurden keine Regeln angegeben gegen die Verstoßen wurde.\r\n"
        if report.user_comment:
            comment_text = f'Kommentar zum Report: "{report.user_comment}"\r\n'
        else:
            comment_text = f"Es wurde kein Kommentar hinzugefügt.\r\n"

        report_url = "https://" + host + report.get_absolute_url()
        link_text = f"Um alle Details zu sehen, geh bitte auf: {report_url}"
        body_text = greeting + new_report_text + reported_rules_text + comment_text + link_text
        message = mail.EmailMessage(subject, body_text, settings.DEFAULT_FROM_EMAIL, [moderator.email])
        print("Sending email to ", moderator.email)
        message.send()
