import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

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
