from django.shortcuts import render, redirect
from django.urls import reverse
from .mail import mail_admins_new_report

from fellchensammlung.models import AdoptionNotice, MarkdownContent, Animal, Rule, Image, Report, ModerationAction, \
    Member
from .forms import AdoptionNoticeForm, AnimalForm, ImageForm, ReportForm


def index(request):
    """View function for home page of site."""
    latest_adoption_list = AdoptionNotice.objects.order_by("-created_at")[:5]
    context = {"adoption_notices": latest_adoption_list}

    return render(request, 'fellchensammlung/index.html', context=context)


def adoption_notice_detail(request, adoption_notice_id):
    adoption_notice = AdoptionNotice.objects.get(id=adoption_notice_id)
    context = {"adoption_notice": adoption_notice}
    return render(request, 'fellchensammlung/details/detail_adoption_notice.html', context=context)


def animal_detail(request, animal_id):
    animal = Animal.objects.get(id=animal_id)
    context = {"animal": animal}
    return render(request, 'fellchensammlung/details/detail_animal.html', context=context)


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
    return render(request, 'fellchensammlung/forms/form_add_adoption.html', {'form': form})


def add_animal_to_adoption(request, adoption_notice_id):
    if request.method == 'POST':
        form = AnimalForm(request.POST)
        image_form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            form.cleaned_data["adoption_notice_id"] = adoption_notice_id
            instance = form.save(commit=False)
            instance.adoption_notice_id = adoption_notice_id

            instance.save()

            if 'image_-image' in request.FILES:
                image = Image(image=request.FILES['image_-image'])
                image.save()
                instance.photos.add(image)

            if "button_add_another_animal" in request.POST:
                return redirect(reverse("add-animal-to-adoption", args=[str(adoption_notice_id)]))
            else:
                return redirect(reverse("adoption-notice-detail", args=[str(adoption_notice_id)]))
    else:
        form = AnimalForm()
        image_form = ImageForm(request.POST, request.FILES, prefix="image_")
    return render(request, 'fellchensammlung/forms/form_add_animal_to_adoption.html',
                  {'form': form, "image_form": image_form})


def about(request):
    rules = Rule.objects.all()
    context = {"rules": rules}
    return render(
        request,
        "fellchensammlung/about.html",
        context=context
    )


def report_adoption(request, adoption_notice_id):
    """
    Form to report adoption notices
    """
    if request.method == 'POST':
        form = ReportForm(request.POST)

        if form.is_valid():
            report_instance = form.save(commit=False)
            report_instance.adoption_notice_id = adoption_notice_id
            report_instance.status = Report.WAITING
            report_instance.save()
            mail_admins_new_report(report_instance)
            return redirect(reverse("report-detail-success", args=[report_instance.pk], ))
    else:
        form = ReportForm()
    return render(request, 'fellchensammlung/forms/form-report.html', {'form': form})


def report_detail(request, report_id, form_complete=False):
    """
    Detailed view of a report, including moderation actions
    """
    report = Report.objects.get(pk=report_id)
    moderation_actions = ModerationAction.objects.filter(report_id=report_id)

    context = {"report": report, "moderation_actions": moderation_actions, "form_complete": form_complete}

    return render(request, 'fellchensammlung/details/detail-report.html', context)


def report_detail_success(request, report_id):
    """
    Calls the report detail view with form_complete set to true, so success message shows
    """
    return report_detail(request, report_id, form_complete=True)


def member_detail(request, user):
    member = Member.objects.get(user=user)
    context = {"member": member}
    return render(request, 'fellchensammlung/details/detail-member.html', context=context)