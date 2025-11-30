from django.urls import path
from .views import (
    AdoptionNoticeApiView,
    AnimalApiView, RescueOrganizationApiView, AddImageApiView, SpeciesApiView, LocationApiView,
    AdoptionNoticeGeoJSONView, RescueOrgGeoJSONView, AdoptionNoticePerOrgApiView, index
)

urlpatterns = [
    path("", index, name="api-base-url"),
    path("adoption_notice", AdoptionNoticeApiView.as_view(), name="api-adoption-notice-list"),
    path("adoption_notice.geojson", AdoptionNoticeGeoJSONView.as_view(), name="api-adoption-notice-list-geojson"),
    path("adoption_notice/<int:id>/", AdoptionNoticeApiView.as_view(), name="api-adoption-notice-detail"),
    path("animals/", AnimalApiView.as_view(), name="api-animal-list"),
    path("animals/<int:id>/", AnimalApiView.as_view(), name="api-animal-detail"),
    path("organizations/", RescueOrganizationApiView.as_view(), name="api-organization-list"),
    path("organizations.geojson", RescueOrgGeoJSONView.as_view(), name="api-organization-list-geojson"),
    path("organizations/<int:id>/", RescueOrganizationApiView.as_view(), name="api-organization-detail"),
    path("organizations/<int:id>/adoption-notices", AdoptionNoticePerOrgApiView.as_view(), name="api-organization-adoption-notices"),
    path("images/", AddImageApiView.as_view(), name="api-add-image"),
    path("species/", SpeciesApiView.as_view(), name="api-species-list"),
    path("locations/", LocationApiView.as_view(), name="api-locations-list"),
]
