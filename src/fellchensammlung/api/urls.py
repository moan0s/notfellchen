from django.urls import path
from .views import (
    AdoptionNoticeApiView
)

urlpatterns = [
    path('adoption_notice', AdoptionNoticeApiView.as_view()),
]
