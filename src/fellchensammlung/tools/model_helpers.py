from django.utils.translation import gettext_lazy as _
from django.db import models

"""
Helpers that MUST NOT DEPEND ON MODELS to avoid circular imports
"""


class NotificationTypeChoices(models.TextChoices):
    NEW_USER = "new_user", _("Useraccount wurde erstellt")
    NEW_REPORT_AN = "new_report_an", _("Vermittlung wurde gemeldet")
    NEW_REPORT_COMMENT = "new_report_comment", _("Kommentar wurde gemeldet")
    AN_IS_TO_BE_CHECKED = "an_is_to_be_checked", _("Vermittlung muss überprüft werden")
    AN_WAS_DEACTIVATED = "an_was_deactivated", _("Vermittlung wurde deaktiviert")
    AN_FOR_SEARCH_FOUND = "an_for_search_found", _("Vermittlung für Suche gefunden")
    NEW_COMMENT = "new_comment", _("Neuer Kommentar")


class NotificationDisplayMapping:
    def __init__(self, email_html_template, email_plain_template, web_partial):
        self.email_html_template = email_html_template
        self.email_plain_template = email_plain_template
        self.web_partial = web_partial


report_mapping = NotificationDisplayMapping(
    email_html_template='fellchensammlung/mail/notifications/report.html',
    email_plain_template='fellchensammlung/mail/notifications/report.txt',
    web_partial="fellchensammlung/partials/notifications/body-new-report.html"
)
# ndm = notification display mapping
ndm = {NotificationTypeChoices.NEW_USER: NotificationDisplayMapping(
    email_html_template='fellchensammlung/mail/notifications/new-user.html',
    email_plain_template="fellchensammlung/mail/notifications/new-user.txt",
    web_partial="fellchensammlung/partials/notifications/body-new-user.html"),
    NotificationTypeChoices.NEW_COMMENT: NotificationDisplayMapping(
        email_html_template='fellchensammlung/mail/notifications/new-comment.html',
        email_plain_template='fellchensammlung/mail/notifications/new-comment.txt',
        web_partial="fellchensammlung/partials/notifications/body-new-comment.html"),
    NotificationTypeChoices.NEW_REPORT_AN: report_mapping,
    NotificationTypeChoices.NEW_REPORT_COMMENT: report_mapping,
    NotificationTypeChoices.AN_IS_TO_BE_CHECKED: NotificationDisplayMapping(
        email_html_template='fellchensammlung/mail/notifications/an-to-be-checked.html',
        email_plain_template='fellchensammlung/mail/notifications/an-to-be-checked.txt',
        web_partial='fellchensammlung/partials/notifications/body-an-to-be-checked.html'
    ),
    NotificationTypeChoices.AN_WAS_DEACTIVATED: NotificationDisplayMapping(
        email_html_template='fellchensammlung/mail/notifications/an-deactivated.html',
        email_plain_template='fellchensammlung/mail/notifications/an-deactivated.txt',
        web_partial='fellchensammlung/partials/notifications/body-an-deactivated.html'
    ),
    NotificationTypeChoices.AN_FOR_SEARCH_FOUND: NotificationDisplayMapping(
        email_html_template='fellchensammlung/mail/notifications/an-for-search-found.html',
        email_plain_template='fellchensammlung/mail/notifications/an-for-search-found.txt',
        web_partial='fellchensammlung/partials/notifications/body-an-for-search.html'
    )
}
