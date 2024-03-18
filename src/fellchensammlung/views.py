from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. Look at all the little guys&girls and non-binary pals!")


def adoption_notice_detail(request, adoption_notice_id):
    return HttpResponse("You're looking at adoption notice %s." % adoption_notice_id)


def animal_detail(request, animal_id):
    response = "You're looking at animal %s."
    return HttpResponse(response % animal_id)
