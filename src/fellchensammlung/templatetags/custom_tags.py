import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from urllib.parse import urlparse

from notfellchen import settings
from fellchensammlung.models import TrustLevel

register = template.Library()


@register.filter('join_link')
def join_link(value, arg):
    """
    Joins the items of value as link to itself together using arg

    The item in values are properly escaped so the safe filter can be applied
    Example usage:
    {%  book.author.all|join_link:", " % | safe}
    """
    from django.utils.html import conditional_escape
    arr = []
    for i in value:
        arr.append('<a href="%s">%s</a>' % (
            i.get_absolute_url(), conditional_escape(i)
        ))

    return arg.join(arr)


@register.filter
def get_type(value):
    return type(value)


@register.filter
@stringfilter
def render_markdown(value):
    md = markdown.Markdown(extensions=["fenced_code"])
    html = md.convert(value)

    return mark_safe(html)


@register.simple_tag
def get_oxitraffic_script_if_enabled():
    if settings.OXITRAFFIC_ENABLED:
        return mark_safe(f'<script type="module" src="https://{settings.OXITRAFFIC_BASE_URL}/count.js"></script>')
    else:
        return ""


@register.filter
@stringfilter
def pointdecimal(value):
    try:
        return f"{float(value):.9f}"
    except ValueError:
        return value


@register.filter
@stringfilter
def domain(url):
    try:
        domain = urlparse(url).netloc
        if domain.startswith("www."):
            return domain[4:]
        return domain
    except ValueError:
        return url


@register.simple_tag
def settings_value(name):
    return getattr(settings, name)


@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


@register.filter
def widget_type(field):
    return field.field.widget.__class__.__name__


@register.filter
def type_to_bulma_class(value):
    if value == "info":
        return "is-info"
    elif value == "warning":
        return "is-warning"
    elif value == "important":
        return "is-danger"
    else:
        return value


@register.simple_tag
def trust_level(level_string):
    return getattr(TrustLevel, level_string)


@register.filter
def dictkey(d, key):
    return d.get(key)
