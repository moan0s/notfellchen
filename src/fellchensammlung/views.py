from django.shortcuts import render

from django.http import HttpResponse
from fellchensammlung.models import AdoptionNotice


def index(request):
    latest_adoption_list = AdoptionNotice.objects.order_by("-created_at")[:5]
    output = ", ".join([q.name for q in latest_adoption_list])
    return HttpResponse(output)


def adoption_notice_detail(request, adoption_notice_id):
    return HttpResponse("You're looking at adoption notice %s." % adoption_notice_id)


def animal_detail(request, animal_id):
    response = "You're looking at animal %s."
    return HttpResponse(response % animal_id)
