from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. Look at all the little guys&girls and non-binary pals!")
