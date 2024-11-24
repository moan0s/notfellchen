from django.urls import path
from .views import (
    AdoptionNoticeApiView,
    AnimalApiView, RescueOrganizationApiView, AddImageApiView, SpeciesApiView
)

urlpatterns = [
    path("adoption_notice", AdoptionNoticeApiView.as_view(), name="api-adoption-notice-list"),
    path("adoption_notice/<int:id>/", AdoptionNoticeApiView.as_view(), name="api-adoption-notice-detail"),
    path("animals/", AnimalApiView.as_view(), name="api-animal-list"),
    path("animals/<int:id>/", AnimalApiView.as_view(), name="api-animal-detail"),
    path("organizations/", RescueOrganizationApiView.as_view(), name="api-organization-list"),
    path("organizations/<int:id>/", RescueOrganizationApiView.as_view(), name="api-organization-detail"),
    path("images/", AddImageApiView.as_view(), name="api-add-image"),
    path("species/", SpeciesApiView.as_view(), name="api-species-list"),
]
