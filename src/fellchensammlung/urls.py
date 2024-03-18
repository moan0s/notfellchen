from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # ex: /animal/5/
    path("<int:animal_id>/", views.animal_detail, name="animal-detail"),
    # ex: /adoption_notice/7/
    path("<int:adoption_notice_id>/", views.adoption_notice_detail, name="adoption-notice-detail"),

    # ex: /search/
    path("suchen/", views.search, name="search"),
    # ex: /vermitteln/
    path("vermitteln/", views.add_adoption, name="add-adoption"),
]