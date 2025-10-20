from django.db.models.enums import TextChoices
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


class AdoptionNoticeStatusChoices:
    class Active(TextChoices):
        SEARCHING = "active_searching", _("Searching")
        INTERESTED = "active_interested", _("Interested")

    class AwaitingAction(TextChoices):
        WAITING_FOR_REVIEW = "awaiting_action_waiting_for_review", _("Waiting for review")
        NEEDS_ADDITIONAL_INFO = "awaiting_action_needs_additional_info", _("Needs additional info")
        UNCHECKED = "awaiting_action_unchecked", _("Unchecked")

    class Closed(TextChoices):
        SUCCESSFUL_WITH_NOTFELLCHEN = "closed_successful_with_notfellchen", _("Successful (with Notfellchen)")
        SUCCESSFUL_WITHOUT_NOTFELLCHEN = "closed_successful_without_notfellchen", _("Successful (without Notfellchen)")
        ANIMAL_DIED = "closed_animal_died", _("Animal died")
        FOR_OTHER_ADOPTION_NOTICE = "closed_for_other_adoption_notice", _("Closed for other adoption notice")
        NOT_OPEN_ANYMORE = "closed_not_open_for_adoption_anymore", _("Not open for adoption anymore")
        LINK_TO_MORE_INFO_NOT_REACHABLE = "closed_link_to_more_info_not_reachable", _(
            "Der Link zu weiteren Informationen ist nicht mehr erreichbar.")
        OTHER = "closed_other", _("Other (closed)")

    class Disabled(TextChoices):
        AGAINST_RULES = "disabled_against_the_rules", _("Against the rules")
        OTHER = "disabled_other", _("Other (disabled)")

    @classmethod
    def all_choices(cls):
        """Return all subgroup choices as a single list for use in models."""
        return (
                cls.Active.choices
                + cls.AwaitingAction.choices
                + cls.Closed.choices
                + cls.Disabled.choices
        )


class AdoptionNoticeStatusChoicesDescriptions:
    _ansc = AdoptionNoticeStatusChoices  # Mapping for readability
    mapping = {_ansc.Active.SEARCHING.value: "",
               _ansc.Active.INTERESTED: _("Jemand hat bereits Interesse an den Tieren."),
               _ansc.Closed.SUCCESSFUL_WITH_NOTFELLCHEN: _("Vermittlung erfolgreich abgeschlossen."),
               _ansc.Closed.SUCCESSFUL_WITHOUT_NOTFELLCHEN: _("Vermittlung erfolgreich abgeschlossen."),
               _ansc.Closed.ANIMAL_DIED: _("Die zu vermittelnden Tiere sind über die Regenbrücke gegangen."),
               _ansc.Closed.FOR_OTHER_ADOPTION_NOTICE: _("Vermittlung wurde zugunsten einer anderen geschlossen."),
               _ansc.Closed.NOT_OPEN_ANYMORE: _("Tier(e) stehen nicht mehr zur Vermittlung bereit."),
               _ansc.Closed.LINK_TO_MORE_INFO_NOT_REACHABLE: _(
                   "Der Link zu weiteren Informationen ist nicht mehr erreichbar,"
                   "die Vermittlung wurde daher automatisch deaktiviert"),
               _ansc.Closed.OTHER: _("Vermittlung geschlossen."),

               _ansc.AwaitingAction.WAITING_FOR_REVIEW: _(
                   "Deaktiviert bis Moderator*innen die Vermittlung prüfen können."),
               _ansc.AwaitingAction.NEEDS_ADDITIONAL_INFO: _("Deaktiviert bis Informationen nachgetragen werden."),
               _ansc.AwaitingAction.UNCHECKED: _(
                   "Vermittlung deaktiviert bis sie vom Team auf Aktualität geprüft wurde."),

               _ansc.Disabled.AGAINST_RULES: _("Vermittlung deaktiviert da sie gegen die Regeln verstößt."),
               _ansc.Disabled.OTHER: _("Vermittlung deaktiviert.")
               }


class AdoptionProcess(TextChoices):
    CONTACT_PERSON_IN_AN = "contact_person_in_an", _("Kontaktiere die Person im Vermittlungstext")


class AdoptionNoticeProcessTemplates:
    _bp = "fellchensammlung/partials/adoption_process/"  # Base path for ease
    mapping = {AdoptionProcess.CONTACT_PERSON_IN_AN: f"{_bp}contact_person_in_an.html",
               }


class RegularCheckStatusChoices(models.TextChoices):
    REGULAR_CHECK = "regular_check", _("Wird regelmäßig geprüft")
    EXCLUDED_NO_ONLINE_LISTING = "excluded_no_online_listing", _("Exkludiert: Tiere werden nicht online gelistet")
    EXCLUDED_OTHER_ORG = "excluded_other_org", _("Exkludiert: Andere Organisation wird geprüft")
    EXCLUDED_SCOPE = "excluded_scope", _("Exkludiert: Organisation hat nie Notfellchen-relevanten Vermittlungen")
    EXCLUDED_OTHER = "excluded_other", _("Exkludiert: Anderer Grund")
