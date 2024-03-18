from django.shortcuts import render

from django.http import HttpResponse
from fellchensammlung.models import AdoptionNotice


def index(request):
    """View function for home page of site."""
    latest_adoption_list = AdoptionNotice.objects.order_by("-created_at")[:5]
    context = {"latest_adoptions": latest_adoption_list}

    return render(request, 'fellchensammlung/index.html', context=context)


def adoption_notice_detail(request, adoption_notice_id):
    return HttpResponse("You're looking at adoption notice %s." % adoption_notice_id)


def animal_detail(request, animal_id):
    response = "You're looking at animal %s."
    return HttpResponse(response % animal_id)

def search(request):
    return render(request, 'fellchensammlung/search.html')
def add_adoption(request):
    return render(request, 'fellchensammlung/add_adoption.html')

