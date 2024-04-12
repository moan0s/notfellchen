import django.conf.global_settings

from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.conf import settings
from django.core import mail
from django.db.models import Q
from fellchensammlung.models import Member
from notfellchen.settings import host


def mail_admins_new_report(report):
    subject = _("New report")
    for moderator in Member.objects.filter(Q(trust_level=Member.MODERATOR) | Q(trust_level=Member.ADMIN)):
        greeting = _("Moin,") + "\r\n"
        new_report_text = _("es wurde eine Vermittlung gemeldet.") + "\r\n"
        if len(report.reported_broken_rules.all()) > 0:
            reported_rules_text = f"Ein Verstoß gegen die folgenden Regeln wurde gemeldet [{', '.join(report.reported_broken_rules.all())}]\r\n"
        else:
            reported_rules_text = f"Es wurden keine Regeln angegeben gegen die Verstoßen wurde.\r\n"
        if report.comment:
            comment_text = f'Kommentar zum Report: "{report.comment}"\r\n'
        else:
            comment_text = f"Es wurde kein Kommentar hinzugefügt.\r\n"

        report_url = "https://" + host + report.get_absolute_url()
        link_text = f"Um alle Details zu sehen, geh bitte auf: {report_url}"
        body_text = greeting + new_report_text + reported_rules_text + comment_text + link_text
        message = mail.EmailMessage(subject, body_text, settings.DEFAULT_FROM_EMAIL, [moderator.user.email])
        print("Sending email to ", moderator.user.email)
        message.send()
