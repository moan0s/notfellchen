from django.urls import path

from . import embeddables

urlpatterns = [
    path("tierschutzorganisationen/<int:rescue_organization_id>/vermittlungen/",
         embeddables.list_ans_per_rescue_organization,
         name="list-adoption-notices-for-rescue-organization"),
    path("tierschutzorganisationen/<int:rescue_organization_id>/vermittlungen/<slug:species_slug>/",
         embeddables.list_ans_per_rescue_organization,
         name="list-adoption-notices-for-rescue-organization-species"),
]
