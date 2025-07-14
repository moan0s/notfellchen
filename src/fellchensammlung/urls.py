from django.urls import path, include

from .forms import CustomRegistrationForm
from .feeds import LatestAdoptionNoticesFeed

from . import views, registration_views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from django.contrib.sitemaps.views import sitemap
from .sitemap import StaticViewSitemap, AdoptionNoticeSitemap, AnimalSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "vermittlungen": AdoptionNoticeSitemap,
    "tiere": AnimalSitemap,
}

urlpatterns = [
    path("", views.index, name="index"),
    path("rss/", LatestAdoptionNoticesFeed(), name="rss"),
    path("metrics/", views.metrics, name="metrics"),
    # ex: /animal/5/edit
    path("tier/<int:animal_id>/edit", views.animal_edit, name="animal-edit"),
    # ex: /animal/5/delete
    path("tier/<int:animal_id>/delete", views.animal_delete, name="animal-delete"),
    # ex: /animal/5/add-photo
    path("tier/<int:animal_id>/add-photo", views.add_photo_to_animal, name="animal-add-photo"),
    # ex: /adoption_notice/7/
    path("vermittlung/<int:adoption_notice_id>/", views.adoption_notice_detail, name="adoption-notice-detail"),
    # ex: /adoption_notice/7/edit
    path("vermittlung/<int:adoption_notice_id>/edit", views.adoption_notice_edit, name="adoption-notice-edit"),
    # ex: /vermittlung/5/add-photo
    path("vermittlung/<int:adoption_notice_id>/add-photo", views.add_photo_to_adoption_notice,
         name="adoption-notice-add-photo"),
    # ex: /adoption_notice/2/add-animal
    path("vermittlung/<int:adoption_notice_id>/add-animal", views.adoption_notice_add_animal,
         name="adoption-notice-add-animal"),
    path("vermittlung/<int:adoption_notice_id>/close", views.deactivate_an,
         name="adoption-notice-close"),

    path("tierschutzorganisationen/", views.list_rescue_organizations, name="rescue-organizations"),
    path("tierschutzorganisationen/<int:rescue_organization_id>/", views.detail_view_rescue_organization,
         name="rescue-organization-detail"),

    # ex: /search/
    path("suchen/", views.search, name="search"),
    path("suchen/<slug:important_location_slug>", views.search_important_locations, name="search-by-location"),
    # ex: /map/
    path("map/", views.map, name="map"),
    # ex: /vermitteln/
    path("vermitteln/", views.add_adoption_notice, name="add-adoption"),

    path("ueber-uns/", views.about, name="about"),
    path("impressum/", views.imprint, name="imprint"),
    path("terms-of-service/", views.terms_of_service, name="terms-of-service"),
    path("datenschutz/", views.privacy, name="privacy"),
    path("ratten-kaufen/", views.buying, name="buying"),

    ################
    ## Moderation ##
    ################
    path("vermittlung/<int:adoption_notice_id>/report", views.report_adoption, name="report-adoption-notice"),

    path("kommentar/<int:comment_id>/report", views.report_comment, name="report-comment"),
    path("meldung/<uuid:report_id>/", views.report_detail, name="report-detail"),
    path("meldung/<uuid:report_id>/sucess", views.report_detail_success, name="report-detail-success"),
    path("modqueue/", views.modqueue, name="modqueue"),

    path("updatequeue/", views.updatequeue, name="updatequeue"),

    path("organization-check/", views.rescue_organization_check, name="organization-check"),
    path("organization-check/dq", views.rescue_organization_check_dq, name="organization-check-dq"),
    path("modtools/", views.moderation_tools_overview, name="modtools"),

    ###########
    ## USERS ##
    ###########
    # ex: user/1
    path("user/<int:user_id>/", views.user_by_id, name="user-detail"),
    path("user/me/", views.my_profile, name="user-me"),
    path("user/notifications/", views.my_notifications, name="user-notifications"),
    path('user/me/export/', views.export_own_profile, name='user-me-export'),

    path('accounts/register/',
         registration_views.HTMLMailRegistrationView.as_view(
             form_class=CustomRegistrationForm,
             email_body_template="fellchensammlung/mail/activation_email.html",
         ),
         name='django_registration_register',
         ),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('change-language', views.change_language, name="change-language"),

    ###########
    ## ADMIN ##
    ###########
    path('instance-health-check', views.instance_health_check, name="instance-health-check"),

    #############
    ## Metrics ##
    #############
    # ex: /metrics
    path('metrics/', views.metrics, name="metrics"),

    #########
    ## API ##
    #########
    path('api/', include('fellchensammlung.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    ###################
    ## External Site ##
    ###################
    path('bulma/external-site/', views.external_site_warning, name="external-site"),

    ###############
    ## TECHNICAL ##
    ###############
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),

]
