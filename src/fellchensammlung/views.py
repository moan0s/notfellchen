import logging

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.core.exceptions import PermissionDenied

from .mail import mail_admins_new_report
from notfellchen import settings

from fellchensammlung import logger
from .models import AdoptionNotice, Text, Animal, Rule, Image, Report, ModerationAction, \
    User, Location, AdoptionNoticeStatus, Subscriptions
from .forms import AdoptionNoticeForm, AdoptionNoticeFormWithDateWidget, ImageForm, ReportAdoptionNoticeForm, \
    CommentForm, ReportCommentForm, AnimalForm, \
    AdoptionNoticeSearchForm, AnimalFormWithDateWidget
from .models import Language, Announcement
from .tools.geo import GeoAPI
from .tools.metrics import gather_metrics_data


def index(request):
    """View function for home page of site."""
    latest_adoption_list = AdoptionNotice.objects.order_by("-created_at")[:5]
    active_adoptions = [adoption for adoption in latest_adoption_list if adoption.is_active]
    language_code = translation.get_language()
    lang = Language.objects.get(languagecode=language_code)
    active_announcements = Announcement.get_active_announcements(lang)
    context = {"adoption_notices": active_adoptions, "announcements": active_announcements}

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

                # Auto-subscribe user to adoption notice
                subscription = Subscriptions(adoption_notice=adoption_notice, user=request.user)
                subscription.save()
        else:
            raise PermissionDenied
    else:
        comment_form = CommentForm(instance=adoption_notice)
    context = {"adoption_notice": adoption_notice, "comment_form": comment_form, "user": request.user}
    return render(request, 'fellchensammlung/details/detail_adoption_notice.html', context=context)


@login_required()
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
    if request.method == 'POST':
        search_form = AdoptionNoticeSearchForm(request.POST)
        max_distance = int(request.POST.get('max_distance'))
        if max_distance == "":
            max_distance = None
        geo_api = GeoAPI()
        search_position = geo_api.get_coordinates_from_query(request.POST['postcode'])

        latest_adoption_list = AdoptionNotice.objects.order_by("-created_at")
        active_adoptions = [adoption for adoption in latest_adoption_list if adoption.is_active]
        adoption_notices_in_distance = [a for a in active_adoptions if a.in_distance(search_position, max_distance)]
        context = {"adoption_notices": adoption_notices_in_distance, "search_form": search_form}
    else:
        latest_adoption_list = AdoptionNotice.objects.order_by("-created_at")
        active_adoptions = [adoption for adoption in latest_adoption_list if adoption.is_active]
        search_form = AdoptionNoticeSearchForm()
        context = {"adoption_notices": active_adoptions, "search_form": search_form}
    return render(request, 'fellchensammlung/search.html', context=context)


@login_required
def add_adoption_notice(request):
    if request.method == 'POST':
        form = AdoptionNoticeFormWithDateWidget(request.POST, request.FILES, in_adoption_notice_creation_flow=True)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            """Search the location given in the location string and add it to the adoption notice"""
            location = Location.get_location_from_string(instance.location_string)
            instance.location = location
            instance.save()

            # Set correct status
            if request.user.trust_level >= User.TRUST_LEVEL[User.COORDINATOR]:
                status = AdoptionNoticeStatus.objects.create(major_status=AdoptionNoticeStatus.ACTIVE,
                                                             minor_status=AdoptionNoticeStatus.MINOR_STATUS_CHOICES[AdoptionNoticeStatus.ACTIVE]["searching"],
                                                             adoption_notice=instance)
                status.save()
            else:
                status = AdoptionNoticeStatus.objects.create(major_status=AdoptionNoticeStatus.AWAITING_ACTION,
                                                             minor_status=AdoptionNoticeStatus.MINOR_STATUS_CHOICES[AdoptionNoticeStatus.AWAITING_ACTION][
                                                                 "waiting_for_review"],
                                                             adoption_notice=instance)
                status.save()

            return redirect(reverse("adoption-notice-add-animal", args=[instance.pk]))
    else:
        form = AdoptionNoticeFormWithDateWidget(in_adoption_notice_creation_flow=True)
    return render(request, 'fellchensammlung/forms/form_add_adoption.html', {'form': form})


@login_required
def adoption_notice_add_animal(request, adoption_notice_id):
    if request.method == 'POST':
        form = AnimalFormWithDateWidget(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.adoption_notice_id = adoption_notice_id
            instance.save()
            form.save_m2m()
            if "save-and-add-another-animal" in request.POST:
                form = AnimalFormWithDateWidget(in_adoption_notice_creation_flow=True)
                return render(request, 'fellchensammlung/forms/form_add_animal_to_adoption.html', {'form': form})
            else:
                return redirect(reverse("adoption-notice-detail", args=[adoption_notice_id]))
    else:
        form = AnimalFormWithDateWidget(in_adoption_notice_creation_flow=True)
    return render(request, 'fellchensammlung/forms/form_add_animal_to_adoption.html', {'form': form})


@login_required
def add_photo_to_animal(request, animal_id):
    animal = Animal.objects.get(id=animal_id)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save()
            animal.photos.add(instance)
            if "save-and-add-another" in request.POST:
                form = ImageForm(in_flow=True)
                return render(request, 'fellchensammlung/forms/form-image.html', {'form': form})
            else:
                return redirect(reverse("animal-detail", args=[animal_id]))
    else:
        form = ImageForm(in_flow=True)
        return render(request, 'fellchensammlung/forms/form-image.html', {'form': form})


@login_required
def add_photo_to_adoption_notice(request, adoption_notice_id):
    adoption_notice = AdoptionNotice.objects.get(id=adoption_notice_id)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save()
            adoption_notice.photos.add(instance)
            if "save-and-add-another" in request.POST:
                form = ImageForm(in_flow=True)
                return render(request, 'fellchensammlung/forms/form-image.html', {'form': form})
            else:
                return redirect(reverse("adoption-notice-detail", args=[adoption_notice_id]))
    else:
        form = ImageForm(in_flow=True)
        return render(request, 'fellchensammlung/forms/form-image.html', {'form': form})


@login_required
def animal_edit(request, animal_id):
    """
    View implements the following methods
    * Updating an Animal
    """
    animal = Animal.objects.get(pk=animal_id)
    if request.method == 'POST':
        form = AnimalForm(request.POST, instance=animal)

        if form.is_valid():
            animal = form.save()
            return redirect(reverse("animal-detail", args=[animal.pk], ))
    else:
        form = AnimalForm(instance=animal)
    return render(request, 'fellchensammlung/forms/form-adoption-notice.html', context={"form": form})


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


def user_detail(request, user_id):
    user = User.objects.get(id=user_id)
    context = {"user": user, "adoption_notices": AdoptionNotice.objects.filter(created_by=user)}
    return render(request, 'fellchensammlung/details/detail-user.html', context=context)


def modqueue(request):
    open_reports = Report.objects.filter(status=Report.WAITING)
    context = {"reports": open_reports}
    return render(request, 'fellchensammlung/modqueue.html', context=context)


def metrics(request):
    data = gather_metrics_data()
    return JsonResponse(data)
