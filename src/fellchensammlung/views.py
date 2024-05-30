import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.core.exceptions import PermissionDenied

from .mail import mail_admins_new_report
from notfellchen import settings

from fellchensammlung import logger
from fellchensammlung.models import AdoptionNotice, Text, Animal, Rule, Image, Report, ModerationAction, \
    Member
from .forms import AdoptionNoticeForm, ImageForm, ReportAdoptionNoticeForm, CommentForm, ReportCommentForm, AnimalForm
from .models import Language


def index(request):
    """View function for home page of site."""
    latest_adoption_list = AdoptionNotice.objects.order_by("-created_at")[:5]
    context = {"adoption_notices": latest_adoption_list}

    return render(request, 'fellchensammlung/index.html', context=context)


def change_language(request):
    if request.method == 'POST':
        language_code = request.POST.get('language')
        if language_code:
            if language_code != settings.LANGUAGE_CODE and language_code in list(zip(*settings.LANGUAGES))[0]:
                redirect_path = f'/{language_code}/'
            elif language_code == settings.LANGUAGE_CODE:
                redirect_path = '/'
            else:
                response = HttpResponseRedirect('/')
                return response
            translation.activate(language_code)
            response = HttpResponseRedirect(redirect_path)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)
    return response


def adoption_notice_detail(request, adoption_notice_id):
    adoption_notice = AdoptionNotice.objects.get(id=adoption_notice_id)
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment_form = CommentForm(request.POST)

            if comment_form.is_valid():
                comment_instance = comment_form.save(commit=False)
                comment_instance.adoption_notice_id = adoption_notice_id
                comment_instance.user = request.user.member
                comment_instance.save()
        else:
            raise PermissionDenied
    else:
        comment_form = CommentForm(instance=adoption_notice)
    context = {"adoption_notice": adoption_notice, "comment_form": comment_form, "user": request.user}
    return render(request, 'fellchensammlung/details/detail_adoption_notice.html', context=context)


def adoption_notice_edit(request, adoption_notice_id):
    """
    Form to update adoption notices
    """
    adoption_notice = AdoptionNotice.objects.get(pk=adoption_notice_id)
    if request.method == 'POST':
        form = AdoptionNoticeForm(request.POST, instance=adoption_notice)

        if form.is_valid():
            adoption_notice_instance = form.save()
            return redirect(reverse("adoption-notice-detail", args=[adoption_notice_instance.pk], ))
    else:
        form = AdoptionNoticeForm(instance=adoption_notice)
    return render(request, 'fellchensammlung/forms/form-adoption-notice.html', context={"form": form})


def animal_detail(request, animal_id):
    animal = Animal.objects.get(id=animal_id)
    context = {"animal": animal}
    return render(request, 'fellchensammlung/details/detail_animal.html', context=context)


def search(request):
    latest_adoption_list = AdoptionNotice.objects.order_by("-created_at")
    context = {"adoption_notices": latest_adoption_list}
    return render(request, 'fellchensammlung/search.html', context=context)


@login_required
def add_adoption(request):
    if request.method == 'POST':
        form = AdoptionNoticeForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save()
            return redirect(reverse("adoption-notice-edit", args=[instance.pk]))
    else:
        form = AdoptionNoticeForm()
    return render(request, 'fellchensammlung/forms/form_add_adoption.html', {'form': form})

@login_required
def adoption_notice_add_animal(request, adoption_notice_id):
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.adoption_notice_id = adoption_notice_id
            instance.save()
            form.save_m2m()
            if True:
                return redirect(reverse("adoption-notice-detail", args=[adoption_notice_id]))
            else:
                return render(request, 'fellchensammlung/forms/form_add_animal_to_adoption.html')
    else:
        form = AnimalForm()
    return render(request, 'fellchensammlung/forms/form_add_animal_to_adoption.html', {'form': form})

@login_required
def edit_adoption_notice(request, animal_id):
    """
    View implements the following methods
    * Updating an AdoptionNotice
    * Adding animals to an AN
    """

    def delete_photo():
        print("Photo deleted")

    def save_photo():
        print("Photo save")

    def add_photo():
        print("Photo added")

    def save_animal():
        print("Animal saved")

    if request.method == 'POST':
        form = AnimalForm(request.POST, animal_id=animal_id, )
        for key in request.POST:
            if key.startswith("delete_photo_"):
                action = delete_photo
            if key.startswith("save_photo_"):
                action = save_photo
            if key.startswith("add_photo"):
                action = add_photo
            if key.startswith("save_animal"):
                action = save_animal

            pk = key.split("_")[-1]

            action(animal_id, pk, form_data=request.POST)

        if form.is_valid():
            animal = form.save()
        return render(request, 'fellchensammlung/forms/form_add_animal_to_adoption.html',
                      {'form': form})

    else:
        form = AnimalForm(animal_id)
        image_form = ImageForm(request.POST, request.FILES, prefix="image_")
    return render(request, 'fellchensammlung/forms/form_add_animal_to_adoption.html',
                  {'form': form})


@login_required
def animal_edit(request, animal_id):
    """
    View implements the following methods
    * Updating an Animal
    * Adding photos to an animal
    """

    def delete_photo():
        print("Photo deleted")

    def save_photo():
        print("Photo save")

    def add_photo():
        print("Photo added")

    def save_animal():
        print("Animal saved")

    if request.method == 'POST':
        form = AnimalForm(request.POST, animal_id=animal_id, )
        for key in request.POST:
            if key.startswith("delete_photo_"):
                action = delete_photo
            if key.startswith("save_photo_"):
                action = save_photo
            if key.startswith("add_photo"):
                action = add_photo
            if key.startswith("save_animal"):
                action = save_animal

            pk = key.split("_")[-1]

            action(animal_id, pk, form_data=request.POST)

        return render(request, 'fellchensammlung/forms/form_add_animal_to_adoption.html',
                      {'form': form})

    else:
        form = AnimalForm(animal_id)
        image_form = ImageForm(request.POST, request.FILES, prefix="image_")
    return render(request, 'fellchensammlung/forms/form_add_animal_to_adoption.html',
                  {'form': form})


def about(request):
    rules = Rule.objects.all()

    language_code = translation.get_language()
    lang = Language.objects.get(languagecode=language_code)

    legal = {}
    for text_code in ["terms_of_service", "privacy_statement", "imprint"]:
        try:
            legal[text_code] = Text.objects.get(text_code=text_code, language=lang, )
        except Text.DoesNotExist:
            legal[text_code] = None

    context = {"rules": rules, }
    context.update(legal)
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
        form = ReportAdoptionNoticeForm(request.POST)

        if form.is_valid():
            report_instance = form.save(commit=False)
            report_instance.adoption_notice_id = adoption_notice_id
            report_instance.status = Report.WAITING
            report_instance.save()
            form.save_m2m()
            mail_admins_new_report(report_instance)
            return redirect(reverse("report-detail-success", args=[report_instance.pk], ))
    else:
        form = ReportAdoptionNoticeForm()
    return render(request, 'fellchensammlung/forms/form-report.html', {'form': form})


def report_comment(request, comment_id):
    """
    Form to report comments
    """
    if request.method == 'POST':
        form = ReportCommentForm(request.POST)

        if form.is_valid():
            report_instance = form.save(commit=False)
            report_instance.reported_comment_id = comment_id
            report_instance.status = Report.WAITING
            report_instance.save()
            form.save_m2m()
            mail_admins_new_report(report_instance)
            return redirect(reverse("report-detail-success", args=[report_instance.pk], ))
    else:
        form = ReportCommentForm()
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


def member_detail(request, user_id):
    member = Member.objects.get(id=user_id)
    context = {"member": member}
    return render(request, 'fellchensammlung/details/detail-member.html', context=context)


def modqueue(request):
    open_reports = Report.objects.filter(status=Report.WAITING)
    context = {"reports": open_reports}
    return render(request, 'fellchensammlung/modqueue.html', context=context)
