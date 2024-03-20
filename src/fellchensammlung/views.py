from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
import markdown

from fellchensammlung.models import AdoptionNotice, MarkdownContent, Animal, Rule, Image
from .forms import AdoptionNoticeForm, AnimalForm


def index(request):
    """View function for home page of site."""
    latest_adoption_list = AdoptionNotice.objects.order_by("-created_at")[:5]
    context = {"adoption_notices": latest_adoption_list}

    return render(request, 'fellchensammlung/index.html', context=context)


def adoption_notice_detail(request, adoption_notice_id):
    adoption_notice = AdoptionNotice.objects.get(id=adoption_notice_id)
    context = {"adoption_notice": adoption_notice}
    return render(request, 'fellchensammlung/detail_adoption_notice.html', context=context)


def animal_detail(request, animal_id):
    animal = Animal.objects.get(id=animal_id)
    context = {"animal": animal}
    return render(request, 'fellchensammlung/detail_animal.html', context=context)


def search(request):
    latest_adoption_list = AdoptionNotice.objects.order_by("-created_at")
    context = {"adoption_notices": latest_adoption_list}
    return render(request, 'fellchensammlung/search.html', context=context)


def add_adoption(request):
    if request.method == 'POST':
        form = AdoptionNoticeForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save()
            return redirect(reverse("add-animal-to-adoption", args=[instance.pk]))
    else:
        form = AdoptionNoticeForm()
    return render(request, 'fellchensammlung/form_add_adoption.html', {'form': form})


def add_animal_to_adoption(request, adoption_notice_id):
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)

        if form.is_valid():
            form.cleaned_data["adoption_notice_id"] = adoption_notice_id
            instance = form.save(commit=False)
            instance.adoption_notice_id = adoption_notice_id

            if 'image' in request.FILES:
                image_instance = Image(image=request.FILES['image'])
                image_instance.save()
                instance.photos.add(image_instance)

            instance.save()
            if "button_add_another_animal" in request.POST:
                return redirect(reverse("add-animal-to-adoption", args=[str(adoption_notice_id)]))
            else:
                return redirect(reverse("adoption-notice-detail", args=[str(adoption_notice_id)]))
    else:
        form = AnimalForm()
    return render(request, 'fellchensammlung/form_add_animal_to_adoption.html', {'form': form})


def about(request):
    rules = Rule.objects.all()
    context = {"rules": rules}
    return render(
        request,
        "fellchensammlung/about.html",
        context=context
    )
