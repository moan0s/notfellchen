from django.template.loader import render_to_string

from fellchensammlung.models import AdoptionNotice


def export_svg(adoption_notice):
    result = render_to_string(template_name="fellchensammlung/images/adoption-notice.svg",
                              context={"adoption_notice": adoption_notice, })
    return result
