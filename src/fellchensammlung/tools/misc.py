import datetime as datetime
import logging

from django.utils.translation import ngettext
from django.utils.translation import gettext as _

from notfellchen import settings
import requests


def pluralize(number, letter="e"):
    try:
        size = len(number)
    except TypeError:
        size = int(number)
    return '' if size == 1 else letter


def age_as_hr_string(age: datetime.timedelta) -> str:
    days = int(age.days)
    weeks = int(age.days / 7)
    months = int(age.days / 30)
    years = int(age.days / 365)
    if years >= 1:
        months = months - 12 * years
        return f'{years:.0f} Jahr{pluralize(years)} und {months:.0f} Monat{pluralize(months)}'
    elif months >= 3:
        return f'{months:.0f} Monat{pluralize(months)}'
    elif weeks >= 3:
        return f'{weeks:.0f} Woche{pluralize(weeks, "n")}'
    else:
        return f'{days:.0f} Tag{pluralize(days)}'


def time_since_as_hr_string(age: datetime.timedelta) -> str:
    days = age.days
    weeks = age.days / 7
    months = age.days / 30
    years = age.days / 365
    minutes = age.seconds / 60
    hours = age.seconds / 3600
    if years >= 1:
        text = ngettext(
            "vor einem Jahr",
            "vor %(years)d Jahren",
            years,
        ) % {
                   "years": years,
               }
    elif months >= 3:
        text = _("vor %(month)d Monaten") % {"month": months}
    elif weeks >= 3:
        text = _("vor %(weeks)d Wochen") % {"weeks": weeks}
    elif days >= 1:
        text = ngettext("vor einem Tag", "vor %(count)d Tagen", days, ) % {"count": days, }
    elif hours >= 1:
        text = ngettext("vor einer Stunde", "vor %(count)d Stunden", hours, ) % {"count": hours, }
    elif minutes >= 1:
        text = ngettext("vor einer Minute", "vor %(count)d Minuten", minutes, ) % {"count": minutes, }
    else:
        text = _("Gerade eben")
    return text


def healthcheck_ok():
    try:
        requests.get(settings.HEALTHCHECKS_URL, timeout=10)
    except requests.RequestException as e:
        logging.error("Ping to healthcheck-server failed: %s" % e)


def is_404(url):
    try:
        result = requests.get(url, timeout=10)
        return result.status_code == 404
    except requests.RequestException as e:
        logging.warning(f"Request to {url} failed: {e}")
