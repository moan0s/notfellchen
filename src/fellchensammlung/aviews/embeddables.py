from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_exempt

from fellchensammlung.aviews.helpers import headers
from fellchensammlung.models import RescueOrganization, AdoptionNotice, Species


@xframe_options_exempt
@headers({"X-Robots-Tag": "noindex"})
def list_ans_per_rescue_organization(request, rescue_organization_id, species_slug=None, active=True):
    expand = request.GET.get("expand")
    background_color = request.GET.get("background_color")
    if expand is not None:
        expand = True
    else:
        expand = False
    org = get_object_or_404(RescueOrganization, pk=rescue_organization_id)

    # Get only active adoption notices or all
    if active:
        adoption_notices_of_org = org.adoption_notices_in_hierarchy_divided_by_status[0]
    else:
        adoption_notices_of_org = org.adoption_notices

    # Filter for Species if necessary
    if species_slug is None:
        adoption_notices = adoption_notices_of_org
    else:
        species = get_object_or_404(Species, slug=species_slug)
        adoption_notices = [adoption_notice for adoption_notice in adoption_notices_of_org if
                            species in adoption_notice.species]

    template = 'fellchensammlung/embeddables/list-adoption-notices.html'
    return render(request, template,
                  context={"adoption_notices": adoption_notices,
                           "expand": expand,
                           "background_color": background_color})
