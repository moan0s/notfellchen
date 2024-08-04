import datetime as datetime


def pluralize(number, letter="e"):
    try:
        size = len(number)
    except TypeError:
        size = int(number)
    return '' if size == 1 else letter


def age_as_hr_string(age: datetime.timedelta) -> str:
    days = age.days
    weeks = age.days/7
    months = age.days/30
    years = age.days/365
    if years >= 1:
        return f'{years:.0f} Jahr{pluralize(years)} und {months:.0} Monat{pluralize(months)}'
    elif months >= 3:
        return f'{months:.0f} Monat{pluralize(months)}'
    elif weeks >= 3:
        return f'{weeks:.0f} Woche{pluralize(weeks, "n")}'
    else:
        return f'{days:.0f} Tag{pluralize(days)}'
