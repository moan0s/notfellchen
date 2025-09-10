from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_exempt

from fellchensammlung.aviews.helpers import headers
from fellchensammlung.models import RescueOrganization, AdoptionNotice, Species


@xframe_options_exempt
@headers({"X-Robots-Tag": "noindex"})
def list_ans_per_rescue_organization(request, rescue_organization_id, species_slug=None):
    expand = request.GET.get("expand")
    if expand is not None:
        expand = True
    else:
        expand = False
    org = get_object_or_404(RescueOrganization, pk=rescue_organization_id)
    if species_slug is None:
        adoption_notices = AdoptionNotice.objects.filter(organization=org)
    else:
        ans_of_rescue_org = AdoptionNotice.objects.filter(organization=org)
        species = get_object_or_404(Species, slug=species_slug)
        adoption_notices = [adoption_notice for adoption_notice in ans_of_rescue_org if species in adoption_notice.species]

    template = 'fellchensammlung/embeddables/list-adoption-notices.html'
    return render(request, template, context={"adoption_notices": adoption_notices, "expand": expand})