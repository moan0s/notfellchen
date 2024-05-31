import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from notfellchen import settings

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
