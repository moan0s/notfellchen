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


class DescriptiveTextChoices(models.TextChoices):
    class Descriptions:
        pass

    @classmethod
    def get_description(cls, value):
        return cls.Descriptions.__getattribute__(value, "")


class AdoptionNoticeStatusChoices:
    class Active(DescriptiveTextChoices):
        SEARCHING = "active_searching", _("Searching")
        INTERESTED = "active_interested", _("Interested")

        class Descriptions:
            SEARCHING = ""
            INTERESTED = _("Jemand hat bereits Interesse an den Tieren.")

    class AwaitingAction(DescriptiveTextChoices):
        WAITING_FOR_REVIEW = "awaiting_action_waiting_for_review", _("Waiting for review")
        NEEDS_ADDITIONAL_INFO = "awaiting_action_needs_additional_info", _("Needs additional info")

        class Descriptions:
            WAITING_FOR_REVIEW = _("Deaktiviert bis Moderator*innen die Vermittlung prüfen können.")
            NEEDS_ADDITIONAL_INFO = _("Deaktiviert bis Informationen nachgetragen werden.")

    class Closed(DescriptiveTextChoices):
        SUCCESSFUL_WITH_NOTFELLCHEN = "closed_successful_with_notfellchen", _("Successful (with Notfellchen)")
        SUCCESSFUL_WITHOUT_NOTFELLCHEN = "closed_successful_without_notfellchen", _("Successful (without Notfellchen)")
        ANIMAL_DIED = "closed_animal_died", _("Animal died")
        FOR_OTHER_ADOPTION_NOTICE = "closed_for_other_adoption_notice", _("Closed for other adoption notice")
        NOT_OPEN_ANYMORE = "closed_not_open_for_adoption_anymore", _("Not open for adoption anymore")
        OTHER = "closed_other", _("Other (closed)")

        class Descriptions:
            SUCCESSFUL_WITH_NOTFELLCHEN = _("Vermittlung erfolgreich abgeschlossen.")
            SUCCESSFUL_WITHOUT_NOTFELLCHEN = _("Vermittlung erfolgreich abgeschlossen.")
            ANIMAL_DIED = _("Die zu vermittelnden Tiere sind über die Regenbrücke gegangen.")
            FOR_OTHER_ADOPTION_NOTICE = _("Vermittlung wurde zugunsten einer anderen geschlossen.")
            NOT_OPEN_ANYMORE = _("Tier(e) stehen nicht mehr zur Vermittlung bereit.")
            OTHER = _("Vermittlung geschlossen.")

    class Disabled(DescriptiveTextChoices):
        AGAINST_RULES = "disabled_against_the_rules", _("Against the rules")
        UNCHECKED = "disabled_unchecked", _("Unchecked")
        OTHER = "disabled_other", _("Other (disabled)")

        class Descriptions:
            AGAINST_RULES = _("Vermittlung deaktiviert da sie gegen die Regeln verstößt.")
            UNCHECKED = _("Vermittlung deaktiviert bis sie vom Team auf Aktualität geprüft wurde.")
            OTHER = _("Vermittlung deaktiviert.")

    @classmethod
    def all_choices(cls):
        """Return all subgroup choices as a single list for use in models."""
        return (
                cls.Active.choices
                + cls.AwaitingAction.choices
                + cls.Closed.choices
                + cls.Disabled.choices
        )

    @classmethod
    def get_description(cls, value):
        """Get description regardless of which subgroup the value belongs to."""
        for subgroup in (cls.Active, cls.AwaitingAction, cls.Closed, cls.Disabled):
            if value in subgroup.values:
                return subgroup.get_description(value)
        return ""
