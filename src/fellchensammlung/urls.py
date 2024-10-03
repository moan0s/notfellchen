from django.urls import path, include
from django_registration.backends.activation.views import RegistrationView

from .forms import CustomRegistrationForm
from .feeds import LatestAdoptionNoticesFeed

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("rss/", LatestAdoptionNoticesFeed(), name="rss"),
    path("metrics/", views.metrics, name="metrics"),
    # ex: /animal/5/
    path("tier/<int:animal_id>/", views.animal_detail, name="animal-detail"),
    # ex: /animal/5/edit
    path("tier/<int:animal_id>/edit", views.animal_edit, name="animal-edit"),
    # ex: /animal/5/add-photo
    path("tier/<int:animal_id>/add-photo", views.add_photo_to_animal, name="animal-add-photo"),
    # ex: /adoption_notice/7/
    path("vermittlung/<int:adoption_notice_id>/", views.adoption_notice_detail, name="adoption-notice-detail"),
    # ex: /adoption_notice/7/edit
    path("vermittlung/<int:adoption_notice_id>/edit", views.adoption_notice_edit, name="adoption-notice-edit"),
    # ex: /vermittlung/5/add-photo
    path("vermittlung/<int:adoption_notice_id>/add-photo", views.add_photo_to_adoption_notice, name="adoption-notice-add-photo"),
    # ex: /adoption_notice/2/add-animal
    path("vermittlung/<int:adoption_notice_id>/add-animal", views.adoption_notice_add_animal, name="adoption-notice-add-animal"),

    # ex: /search/
    path("suchen/", views.search, name="search"),
    # ex: /map/
    path("map/", views.map, name="map"),
    # ex: /vermitteln/
    path("vermitteln/", views.add_adoption_notice, name="add-adoption"),

    path("ueber-uns/", views.about, name="about"),

    ################
    ## Moderation ##
    ################
    path("vermittlung/<int:adoption_notice_id>/report", views.report_adoption, name="report-adoption-notice"),

    path("kommentar/<int:comment_id>/report", views.report_comment, name="report-comment"),
    path("meldung/<uuid:report_id>/", views.report_detail, name="report-detail"),
    path("meldung/<uuid:report_id>/sucess", views.report_detail_success, name="report-detail-success"),
    path("modqueue/", views.modqueue, name="modqueue"),
    
    path("updatequeue/", views.updatequeue, name="updatequeue"),

    ###########
    ## USERS ##
    ###########
    # ex: user/1
    path("user/<int:user_id>/", views.user_detail, name="user-detail"),

    path('accounts/register/',
         RegistrationView.as_view(
             form_class=CustomRegistrationForm
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


]
