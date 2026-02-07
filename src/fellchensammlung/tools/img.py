from django.template.loader import render_to_string

from fellchensammlung.models import AdoptionNotice


def export_svg(adoption_notice, template_name: str = "fellchensammlung/images/adoption-notice.svg"):
    result = render_to_string(template_name=template_name,
                              context={"adoption_notice": adoption_notice, })
    return result
