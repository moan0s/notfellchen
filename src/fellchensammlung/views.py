import logging
from datetime import timedelta

from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.http.response import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import translation, timezone
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from django.core.serializers import serialize
from django.utils.translation import gettext_lazy as _
import json
import requests

from .mail import notify_mods_new_report
from notfellchen import settings

from fellchensammlung import logger
from .models import AdoptionNotice, Text, Animal, Rule, Image, Report, ModerationAction, \
    User, Location, AdoptionNoticeStatus, Subscriptions, Notification, RescueOrganization, \
    Species, Log, Timestamp, TrustLevel, SexChoicesWithAll, SearchSubscription, \
    ImportantLocation, SpeciesSpecificURL, NotificationTypeChoices, SocialMediaPost
from .forms import AdoptionNoticeForm, ImageForm, ReportAdoptionNoticeForm, \
    CommentForm, ReportCommentForm, AnimalForm, AdoptionNoticeFormAutoAnimal, SpeciesURLForm, RescueOrgInternalComment
from .models import Language, Announcement
from .tools import i18n
from .tools.fedi import post_an_to_fedi
from .tools.geo import GeoAPI, zoom_level_for_radius
from .tools.metrics import gather_metrics_data
from .tools.admin import clean_locations, get_unchecked_adoption_notices, deactivate_unchecked_adoption_notices, \
    deactivate_404_adoption_notices, send_test_email
from .tasks import post_adoption_notice_save
from rest_framework.authtoken.models import Token

from .tools.search import Search


def user_is_trust_level_or_above(user, trust_level=TrustLevel.MODERATOR):
    return user.is_authenticated and user.trust_level >= trust_level


def user_is_owner_or_trust_level(user, django_object, trust_level=TrustLevel.MODERATOR):
    """
    Checks if a user is either the owner of a record or has a trust level equal or higher than the given one
    """
    return user.is_authenticated and (
            user.trust_level >= trust_level or django_object.owner == user)


def fail_if_user_not_owner_or_trust_level(user, django_object, trust_level=TrustLevel.MODERATOR):
    if not user_is_owner_or_trust_level(user, django_object, trust_level):
        raise PermissionDenied


def index(request):
    """View function for home page of site."""
    latest_adoption_list = AdoptionNotice.objects.filter(
        adoptionnoticestatus__major_status=AdoptionNoticeStatus.ACTIVE).order_by("-created_at")
    active_adoptions = [adoption for adoption in latest_adoption_list if adoption.is_active]
    language_code = translation.get_language()
    lang = Language.objects.get(languagecode=language_code)
    active_announcements = Announcement.get_active_announcements(lang)

    context = {"adoption_notices": active_adoptions[:4], "show_ANs": True,
               "announcements": active_announcements}
    Text.get_texts(["how_to", "introduction"], lang, context)

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
        return render(request, "fellchensammlung/errors/403.html", status=403)


def handle_an_check_actions(request, action, adoption_notice=None):
    if adoption_notice is None:
        adoption_notice = AdoptionNotice.objects.get(id=request.POST.get("adoption_notice_id"))
    edit_permission = request.user == adoption_notice.owner or user_is_trust_level_or_above(request.user,
                                                                                            TrustLevel.MODERATOR)

    # Check if the user is permitted to perform the actions
    if action in ("checked_inactive", "checked_active") and not request.user.is_authenticated or not edit_permission:
        return render(request, "fellchensammlung/errors/403.html", status=403)

    if action == "checked_inactive":
        adoption_notice.set_closed()
    elif action == "checked_active":
        adoption_notice.set_active()
    return None


def adoption_notice_detail(request, adoption_notice_id):
    adoption_notice = get_object_or_404(AdoptionNotice, id=adoption_notice_id)
    adoption_notice_meta = adoption_notice._meta
    if request.user.is_authenticated:
        try:
            subscription = Subscriptions.objects.get(owner=request.user, adoption_notice=adoption_notice)
            is_subscribed = True
        except Subscriptions.DoesNotExist:
            is_subscribed = False
    else:
        is_subscribed = False
    has_edit_permission = user_is_owner_or_trust_level(request.user, adoption_notice)
    if request.method == 'POST':
        action = request.POST.get("action")
        handle_an_check_actions(request, action, adoption_notice)
        if request.user.is_authenticated:
            if action == "comment":
                comment_form = CommentForm(request.POST)

                if comment_form.is_valid():
                    comment_instance = comment_form.save(commit=False)
                    comment_instance.adoption_notice_id = adoption_notice_id
                    comment_instance.user = request.user
                    comment_instance.save()

                    """Log"""
                    Log.objects.create(user=request.user, action="comment",
                                       text=f"{request.user} hat Kommentar {comment_instance.pk} zur Vermittlung {adoption_notice_id} hinzugefügt")

                    # Auto-subscribe user to adoption notice
                    subscription, created = Subscriptions.objects.get_or_create(adoption_notice=adoption_notice,
                                                                                owner=request.user)
                    subscription.save()

                    # Notify users that a comment was added
                    for subscription in adoption_notice.get_subscriptions():
                        # Create a notification but only if the user is not the one that posted the comment
                        if subscription.owner != request.user:
                            notification = Notification(user_to_notify=subscription.owner,
                                                        adoption_notice=adoption_notice,
                                                        notification_type=NotificationTypeChoices.NEW_COMMENT,
                                                        title=f"{adoption_notice.name} - Neuer Kommentar",
                                                        text=f"{request.user}: {comment_instance.text}",
                                                        comment=comment_instance)
                            notification.save()
            else:
                comment_form = CommentForm(instance=adoption_notice)
            if action == "subscribe":
                Subscriptions.objects.create(owner=request.user, adoption_notice=adoption_notice)
                is_subscribed = True
            if action == "unsubscribe":
                subscription.delete()
                is_subscribed = False
        elif action == "subscribe":
            return redirect_to_login(next=request.path)
        else:
            return HttpResponseForbidden()
    else:
        comment_form = CommentForm(instance=adoption_notice)
    context = {"adoption_notice": adoption_notice, "comment_form": comment_form, "user": request.user,
               "has_edit_permission": has_edit_permission, "is_subscribed": is_subscribed,
               "adoption_notice_meta": adoption_notice_meta}
    return render(request, 'fellchensammlung/details/detail-adoption-notice.html', context=context)


@login_required()
def adoption_notice_edit(request, adoption_notice_id):
    """
    Form to update adoption notices
    """
    adoption_notice = AdoptionNotice.objects.get(pk=adoption_notice_id)
    fail_if_user_not_owner_or_trust_level(request.user, adoption_notice)
    if request.method == 'POST':
        form = AdoptionNoticeForm(request.POST, instance=adoption_notice)

        if form.is_valid():
            adoption_notice_instance = form.save()
            """Search the location given in the location string and add it to the adoption notice"""
            location = Location.get_location_from_string(adoption_notice_instance.location_string)
            adoption_notice_instance.location = location
            adoption_notice_instance.save()

            """Log"""
            Log.objects.create(user=request.user, action="adoption_notice_edit",
                               text=f"{request.user} hat Vermittlung {adoption_notice.pk} geändert")
            return redirect(reverse("adoption-notice-detail", args=[adoption_notice_instance.pk], ))
    else:
        form = AdoptionNoticeForm(instance=adoption_notice)
    return render(request, 'fellchensammlung/forms/form-adoption-notice-basic.html', context={"form": form})


def search_important_locations(request, important_location_slug):
    i_location = get_object_or_404(ImportantLocation, slug=important_location_slug)
    search = Search()
    search.search_from_predefined_i_location(i_location)

    site_title = _("Ratten in %(location_name)s") % {"location_name": i_location.name}
    site_description = _("Ratten in Tierheimen und Rattenhilfen in der Nähe von %(location_name)s suchen.") % {
        "location_name": i_location.name}
    canonical_url = reverse("search-by-location", args=[i_location.slug])

    context = {"adoption_notices": search.get_adoption_notices(),
               "search_form": search.search_form,
               "place_not_found": search.place_not_found,
               "subscribed_search": None,
               "searched": False,
               "map_center": search.position,
               "search_center": search.position,
               "map_pins": [search],
               "location": search.location,
               "search_radius": search.max_distance,
               "zoom_level": zoom_level_for_radius(search.max_distance),
               "geocoding_api_url": settings.GEOCODING_API_URL,
               "show_ANs": True,
               "site_title": site_title,
               "site_description": site_description,
               "canonical_url": canonical_url}
    return render(request, 'fellchensammlung/search.html', context=context)


def search(request, templatename="fellchensammlung/search.html"):
    # A user just visiting the search site did not search, only upon completing the search form a user has really
    # searched. This will toggle the "subscribe" button
    searched = False
    search = Search()
    search.search_from_request(request)
    if request.method == 'POST':
        searched = True
        if "subscribe_to_search" in request.POST:
            # Make sure user is logged in
            if not request.user.is_authenticated:
                return redirect_to_login(next=request.path)
            search.subscribe(request.user)
        if "unsubscribe_to_search" in request.POST:
            if not request.user.is_authenticated:
                return redirect_to_login(next=request.path)
            search_subscription = SearchSubscription.objects.get(pk=request.POST["unsubscribe_to_search"])
            if search_subscription.owner == request.user:
                search_subscription.delete()
            else:
                raise PermissionDenied
    if request.user.is_authenticated:
        subscribed_search = search.get_subscription_or_none(request.user)
    else:
        subscribed_search = None
    site_title = _("Suche")
    site_description = _("Ratten in Tierheimen und Rattenhilfen in der Nähe suchen.")
    canonical_url = reverse("search")

    context = {"adoption_notices": search.get_adoption_notices(),
               "search_form": search.search_form,
               "place_not_found": search.place_not_found,
               "subscribed_search": subscribed_search,
               "searched": searched,
               "map_center": search.position,
               "search_center": search.position,
               "map_pins": [search],
               "location": search.location,
               "search_radius": search.max_distance,
               "zoom_level": zoom_level_for_radius(search.max_distance),
               "geocoding_api_url": settings.GEOCODING_API_URL,
               "show_ANs": True,
               "site_title": site_title,
               "site_description": site_description,
               "canonical_url": canonical_url}
    return render(request, templatename, context=context)


@login_required
def add_adoption_notice(request):
    if request.method == 'POST':
        form = AdoptionNoticeFormAutoAnimal(request.POST)

        if form.is_valid():
            an_instance = form.save(commit=False)
            an_instance.owner = request.user

            if request.user.trust_level >= TrustLevel.MODERATOR:
                an_instance.set_active()
            else:
                an_instance.set_unchecked()

            # Get the species and number of animals from the form
            species = form.cleaned_data["species"]
            sex = form.cleaned_data["sex"]
            num_animals = form.cleaned_data["num_animals"]
            date_of_birth = form.cleaned_data["date_of_birth"]
            for i in range(0, num_animals):
                Animal.objects.create(owner=request.user,
                                      name=f"{species} {i + 1}", adoption_notice=an_instance, species=species, sex=sex,
                                      date_of_birth=date_of_birth)

            """Log"""
            Log.objects.create(user=request.user, action="add_adoption_notice",
                               text=f"{request.user} hat Vermittlung {an_instance.pk} hinzugefügt")

            """Spin up a task that adds the location and notifies search subscribers"""
            post_adoption_notice_save.delay(an_instance.id)

            """Subscriptions"""
            # Automatically subscribe user that created AN to AN
            Subscriptions.objects.create(owner=request.user, adoption_notice=an_instance)

            return redirect(reverse("adoption-notice-detail", args=[an_instance.pk]))
        else:
            print(form.errors)
    else:
        form = AdoptionNoticeFormAutoAnimal()
    return render(request, 'fellchensammlung/forms/form-add-adoption.html', {'form': form})


@login_required
def adoption_notice_add_animal(request, adoption_notice_id):
    # Only users that are mods or owners of the adoption notice are allowed to add to it
    adoption_notice = AdoptionNotice.objects.get(pk=adoption_notice_id)
    fail_if_user_not_owner_or_trust_level(request.user, adoption_notice)
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.adoption_notice_id = adoption_notice_id
            instance.owner = request.user
            instance.save()
            form.save_m2m()
            if "save-and-add-another-animal" in request.POST:
                form = AnimalForm()
                return render(request, 'fellchensammlung/forms/form-add-animal-to-adoption.html', {'form': form})
            else:
                return redirect(reverse("adoption-notice-detail", args=[adoption_notice_id]))
    else:
        form = AnimalForm()
    return render(request, 'fellchensammlung/forms/form-add-animal-to-adoption.html', {'form': form})


@login_required
def add_photo_to_animal(request, animal_id):
    animal = Animal.objects.get(id=animal_id)
    # Only users that are mods or owners of the animal are allowed to add to it
    fail_if_user_not_owner_or_trust_level(request.user, animal)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()

            animal.photos.add(instance)

            """Log"""
            Log.objects.create(user=request.user, action="add_photo_to_animal",
                               text=f"{request.user} hat Foto {instance.pk} zum Tier {animal.pk} hinzugefügt")

            if "save-and-add-another" in request.POST:
                form = ImageForm(in_flow=True)
                return render(request, 'fellchensammlung/forms/form-image.html', {'form': form})
            else:
                return redirect(reverse("adoption-notice-detail", args=[animal.adoption_notice.pk], ))
        else:
            return render(request, 'fellchensammlung/forms/form-image.html', {'form': form})

    else:
        form = ImageForm(in_flow=True)
        return render(request, 'fellchensammlung/forms/form-image.html', {'form': form})


@login_required
def add_photo_to_adoption_notice(request, adoption_notice_id):
    adoption_notice = AdoptionNotice.objects.get(id=adoption_notice_id)
    # Only users that are mods or owners of the adoption notice are allowed to add to it
    fail_if_user_not_owner_or_trust_level(request.user, adoption_notice)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            adoption_notice.photos.add(instance)
            """Log"""
            Log.objects.create(user=request.user, action="add_photo_to_animal",
                               text=f"{request.user} hat Foto {instance.pk} zur Vermittlung {adoption_notice.pk} hinzugefügt")
            if "save-and-add-another" in request.POST:
                form = ImageForm(in_flow=True)
                return render(request, 'fellchensammlung/forms/form-image.html', {'form': form})
            else:
                return redirect(reverse("adoption-notice-detail", args=[adoption_notice_id]))
        else:
            return render(request, 'fellchensammlung/forms/form-image.html', {'form': form})
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
    # Only users that are mods or owners of the animal are allowed to edit it
    fail_if_user_not_owner_or_trust_level(request.user, animal)
    if request.method == 'POST':
        form = AnimalForm(request.POST, instance=animal)

        if form.is_valid():
            animal = form.save()

            """Log"""
            Log.objects.create(user=request.user, action="add_photo_to_animal",
                               text=f"{request.user} hat Tier {animal.pk} zum Tier geändert")
            return redirect(reverse("adoption-notice-detail", args=[animal.adoption_notice.pk], ))
    else:
        form = AnimalForm(instance=animal)
    return render(request, 'fellchensammlung/forms/form-animal.html',
                  context={"form": form, "animal": animal})


@login_required
def animal_delete(request, animal_id):
    """
    Shows a conformation page from which a user can delete an animal or go back to the adoption notice.
    """
    animal = Animal.objects.get(pk=animal_id)
    # Only users that are mods or owners of the animal are allowed to edit it
    fail_if_user_not_owner_or_trust_level(request.user, animal)
    if request.method == 'POST':
        if "delete" in request.POST:
            # First delete related images, then animal
            images = animal.get_photos()
            for image in images:
                image.delete()
            animal.delete()
            """Log"""
            Log.objects.create(user=request.user, action="delete_animal",
                               text=f"{request.user} hat Tier {animal.pk} gelöscht")
            return redirect(reverse("adoption-notice-detail", args=[animal.adoption_notice.pk], ))
    return render(request, 'fellchensammlung/forms/form-delete-animal.html', context={"animal": animal})


def about(request):
    context = i18n.get_texts_by_language(["about_us", "faq"])

    return render(
        request,
        "fellchensammlung/about.html",
        context=context
    )


def render_text(request, text):
    context = {"text": text}

    return render(
        request,
        "fellchensammlung/one-text.html",
        context=context
    )


def imprint(request):
    text = i18n.get_text_by_language("imprint")
    return render_text(request, text)


def privacy(request):
    text = i18n.get_text_by_language("privacy_statement")
    return render_text(request, text)


def buying(request):
    text = i18n.get_text_by_language("buying")
    return render_text(request, text)


def terms_of_service(request):
    text = i18n.get_text_by_language("terms_of_service")
    rules = Rule.objects.all()
    context = {"rules": rules, "text": text}
    return render(
        request,
        "fellchensammlung/terms-of-service.html",
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
            notify_mods_new_report(report_instance, NotificationTypeChoices.NEW_REPORT_AN)
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
            notify_mods_new_report(report_instance, NotificationTypeChoices.NEW_REPORT_COMMENT)
            return redirect(reverse("report-detail-success", args=[report_instance.pk], ))
    else:
        form = ReportCommentForm()
    return render(request, 'fellchensammlung/forms/form-report.html', {'form': form})


def report_detail(request, report_id, form_complete=False):
    """
    Detailed view of a report, including moderation actions
    """
    # Prefetching reduces the number of queries to the database that are needed (see reported_content)
    report = Report.objects.select_related("reportadoptionnotice", "reportcomment").get(pk=report_id)
    moderation_actions = ModerationAction.objects.filter(report_id=report_id)
    is_mod_or_above = user_is_trust_level_or_above(request.user, TrustLevel.MODERATOR)

    context = {"report": report, "moderation_actions": moderation_actions,
               "form_complete": form_complete, "is_mod_or_above": is_mod_or_above}

    return render(request, 'fellchensammlung/details/detail-report.html', context)


def report_detail_success(request, report_id):
    """
    Calls the report detail view with form_complete set to true, so success message shows
    """
    return report_detail(request, report_id, form_complete=True)


def user_detail(request, user, token=None):
    context = {"user": user,
               "adoption_notices": AdoptionNotice.objects.filter(owner=user),
               "notifications": Notification.objects.filter(user_to_notify=user, read=False),
               "search_subscriptions": SearchSubscription.objects.filter(owner=user), }
    if token is not None:
        context["token"] = token
    return render(request, 'fellchensammlung/details/detail-user.html', context=context)


@login_required
def user_by_id(request, user_id):
    user = User.objects.get(id=user_id)
    # Only users that are mods or owners of the user are allowed to view
    fail_if_user_not_owner_or_trust_level(user=request.user, django_object=user, trust_level=TrustLevel.MODERATOR)
    if user == request.user:
        return my_profile(request)
    else:
        return user_detail(request, user)


def process_notification_actions(request, action):
    """
    As multiple views allow to mark notifications as read, this function can be used to process these actions

    The function allows users to mark only their own notifications as read.
    """
    if action == "notification_mark_read":
        notification_id = request.POST.get("notification_id")

        notification = Notification.objects.get(pk=notification_id)
        # Ensures a user can only mark their own notifications as read
        if not notification.user_to_notify == request.user:
            return render(request, "fellchensammlung/errors/403.html", status=403)
        notification.mark_read()
    elif action == "notification_mark_all_read":
        notifications = Notification.objects.filter(user_to_notify=request.user, read=False)
        for notification in notifications:
            notification.mark_read()
    return None


@login_required()
def my_profile(request):
    if request.method == 'POST':
        if "create_token" in request.POST:
            Token.objects.create(user=request.user)
        elif "delete_token" in request.POST:
            Token.objects.get(user=request.user).delete()
        elif "toggle_email_notifications" in request.POST:
            user = request.user
            user.email_notifications = not user.email_notifications
            user.save()

        action = request.POST.get("action")
        process_notification_actions(request, action)
        if action == "search_subscription_delete":
            search_subscription_id = request.POST.get("search_subscription_id")
            SearchSubscription.objects.get(pk=search_subscription_id).delete()
            logging.info(f"Deleted subscription {search_subscription_id}")

    try:
        token = Token.objects.get(user=request.user)
    except Token.DoesNotExist:
        token = None
    return user_detail(request, request.user, token)


@login_required()
def my_notifications(request):
    if request.method == 'POST':
        action = request.POST.get("action")
        process_notification_actions(request, action)

    context = {"notifications_unread": Notification.objects.filter(user_to_notify=request.user, read=False).order_by(
        "-created_at"),
        "notifications_read_last": Notification.objects.filter(user_to_notify=request.user,
                                                               read=True).order_by("-read_at")}
    return render(request, 'fellchensammlung/notifications.html', context=context)


@user_passes_test(user_is_trust_level_or_above)
def modqueue(request):
    open_reports = Report.objects.select_related("reportadoptionnotice", "reportcomment").filter(status=Report.WAITING)
    context = {"reports": open_reports}
    return render(request, 'fellchensammlung/modqueue.html', context=context)


@login_required
def updatequeue(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # This function handles the activation and deactivation of ANs
        # Separate function because it's used in multiple places
        handle_an_check_actions(request, action)

    if user_is_trust_level_or_above(request.user, TrustLevel.MODERATOR):
        last_checked_adoption_list = AdoptionNotice.objects.order_by("last_checked")
    else:
        last_checked_adoption_list = AdoptionNotice.objects.filter(owner=request.user).order_by("last_checked")
    adoption_notices_active = [adoption for adoption in last_checked_adoption_list if adoption.is_active]
    adoption_notices_disabled = [adoption for adoption in last_checked_adoption_list if adoption.is_disabled_unchecked]
    context = {"adoption_notices_disabled": adoption_notices_disabled,
               "adoption_notices_active": adoption_notices_active}
    return render(request, 'fellchensammlung/updatequeue.html', context=context)


def map(request):
    context = {"show_ANs": True,
               "show_rescue_orgs": True}

    return render(request, 'fellchensammlung/map.html', context=context)


def metrics(request):
    data = gather_metrics_data()
    return JsonResponse(data)


@login_required
def instance_health_check(request):
    """
    Allows an administrator to check common problems of an instance
    """
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "clean_locations":
            clean_locations(quiet=False)
        elif action == "deactivate_unchecked_adoption_notices":
            deactivate_unchecked_adoption_notices()
        elif action == "deactivate_404":
            deactivate_404_adoption_notices()
        elif action == "send_test_email":
            target_email = request.POST.get("test_email_address")
            send_test_email(target_email)

    number_of_adoption_notices = AdoptionNotice.objects.all().count()
    none_geocoded_adoption_notices = AdoptionNotice.objects.filter(location__isnull=True)
    number_not_geocoded_adoption_notices = len(none_geocoded_adoption_notices)

    number_of_rescue_orgs = RescueOrganization.objects.all().count()
    none_geocoded_rescue_orgs = RescueOrganization.objects.filter(location__isnull=True)
    number_not_geocoded_rescue_orgs = len(none_geocoded_rescue_orgs)

    unchecked_ans = get_unchecked_adoption_notices()
    number_unchecked_ans = len(unchecked_ans)

    # CHECK FOR MISSING TEXTS
    languages = Language.objects.all()
    texts = Text.objects.all()
    text_codes = set([text.text_code for text in texts])
    missing_texts = []
    for language in languages:
        for text_code in text_codes:
            try:
                Text.objects.get(text_code=text_code, language=language)
            except Text.DoesNotExist:
                missing_texts.append((text_code, language))

    # Timestamps
    timestamps = Timestamp.objects.all()

    context = {
        "number_of_adoption_notices": number_of_adoption_notices,
        "number_not_geocoded_adoption_notices": number_not_geocoded_adoption_notices,
        "none_geocoded_adoption_notices": none_geocoded_adoption_notices,
        "number_of_rescue_orgs": number_of_rescue_orgs,
        "number_not_geocoded_rescue_orgs": number_not_geocoded_rescue_orgs,
        "none_geocoded_rescue_orgs": none_geocoded_rescue_orgs,
        "missing_texts": missing_texts,
        "number_unchecked_ans": number_unchecked_ans,
        "unchecked_ans": unchecked_ans,
        "timestamps": timestamps
    }

    return render(request, 'fellchensammlung/instance-health-check.html', context=context)


def external_site_warning(request, template_name='fellchensammlung/external-site-warning.html'):
    url = request.GET.get("url")
    context = {"url": url}
    language_code = translation.get_language()
    lang = Language.objects.get(languagecode=language_code)
    texts = Text.get_texts(["external_site_warning", "good_adoption_practices"], language=lang)
    context.update(texts)

    return render(request, template_name, context=context)


def list_rescue_organizations(request, species=None, template='fellchensammlung/animal-shelters.html'):
    if species is None:
        rescue_organizations = RescueOrganization.objects.all()
    else:
        rescue_organizations = RescueOrganization.objects.filter(specializations=species)

    paginator = Paginator(rescue_organizations, 10)

    page_number = request.GET.get("page")
    if page_number is None:
        page_number = 1
    else:
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1

    rescue_organizations_to_list = paginator.get_page(page_number)
    context = {"rescue_organizations_to_list": rescue_organizations_to_list,
               "show_rescue_orgs": True,
               "elided_page_range": paginator.get_elided_page_range(page_number, on_each_side=2, on_ends=1)}
    return render(request, template, context=context)


def specialized_rescues(request, species_id):
    species = get_object_or_404(Species, pk=species_id)
    return list_rescue_organizations(request, species)


def detail_view_rescue_organization(request, rescue_organization_id,
                                    template='fellchensammlung/details/detail-rescue-organization.html'):
    org = RescueOrganization.objects.get(pk=rescue_organization_id)
    org_meta = org._meta
    return render(request, template,
                  context={"org": org, "map_center": org.position, "zoom_level": 6, "map_pins": [org],
                           "org_meta": org_meta})


def export_own_profile(request):
    user = request.user
    ANs = AdoptionNotice.objects.filter(owner=user)
    user_as_json = serialize('json', [user])
    user_editable = json.loads(user_as_json)
    user_editable[0]["fields"]["password"] = "Password hash redacted for security reasons"
    user_as_json = json.dumps(user_editable)
    ANs_as_json = serialize('json', ANs)
    full_json = f"{user_as_json}, {ANs_as_json}"
    return HttpResponse(full_json, content_type="application/json")


@login_required
def rescue_organization_check(request, context=None):
    if context is None:
        context = {}
    if request.method == "POST":
        rescue_org = RescueOrganization.objects.get(id=request.POST.get("rescue_organization_id"))
        edit_permission = user_is_trust_level_or_above(request.user, TrustLevel.MODERATOR)
        if not edit_permission:
            return render(request, "fellchensammlung/errors/403.html", status=403)
        action = request.POST.get("action")
        if action == "checked":
            rescue_org.set_checked()
        elif action == "exclude":
            rescue_org.set_exclusion_from_checks()
        elif action == "set_species_url":
            species_url_form = SpeciesURLForm(request.POST)

            if species_url_form.is_valid():
                species_url_instance = species_url_form.save(commit=False)
                species_url_instance.rescue_organization_id = rescue_org.id
                species_url_instance.save()
        elif action == "update_internal_comment":
            comment_form = RescueOrgInternalComment(request.POST, instance=rescue_org)
            if comment_form.is_valid():
                comment_form.save()

    rescue_orgs_to_check = RescueOrganization.objects.filter(exclude_from_check=False,
                                                             ongoing_communication=False).order_by("last_checked")[:3]
    rescue_orgs_with_ongoing_communication = RescueOrganization.objects.filter(ongoing_communication=True).order_by(
        "updated_at")
    rescue_orgs_last_checked = RescueOrganization.objects.filter().order_by("-last_checked")[:10]
    rescue_orgs_to_comment = rescue_orgs_to_check | rescue_orgs_with_ongoing_communication | rescue_orgs_last_checked
    # Prepare a form for each organization
    comment_forms = {
        org.id: RescueOrgInternalComment(instance=org) for org in rescue_orgs_to_comment
    }

    timeframe = timezone.now().date() - timedelta(days=14)
    num_rescue_orgs_to_check = RescueOrganization.objects.filter(exclude_from_check=False).filter(
        last_checked__lt=timeframe).count()
    num_rescue_orgs_checked = RescueOrganization.objects.filter(exclude_from_check=False).filter(
        last_checked__gte=timeframe).count()

    try:
        percentage_checked = 100 * num_rescue_orgs_checked / (num_rescue_orgs_to_check + num_rescue_orgs_checked)
    except ZeroDivisionError:
        percentage_checked = 100

    context["rescue_orgs_to_check"] = rescue_orgs_to_check
    context["rescue_orgs_last_checked"] = rescue_orgs_last_checked
    context["comment_forms"] = comment_forms
    context["num_rescue_orgs_to_check"] = num_rescue_orgs_to_check
    context["percentage_checked"] = percentage_checked
    context["num_rescue_orgs_checked"] = num_rescue_orgs_checked
    context["rescue_orgs_with_ongoing_communication"] = rescue_orgs_with_ongoing_communication
    context["set_internal_comment_available"] = True
    return render(request, 'fellchensammlung/rescue-organization-check.html', context=context)


@login_required
def rescue_organization_check_dq(request):
    """
    Modified view to allow setting species specific urls
    DQ = data quality
    """
    context = {"set_species_url_available": True,
               "dq": True,
               "species_url_form": SpeciesURLForm,
               "internal_comment_form": RescueOrgInternalComment}
    return rescue_organization_check(request, context)


@user_passes_test(user_is_trust_level_or_above)
def moderation_tools_overview(request):
    context = None
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "post_to_fedi":
            adoption_notice = SocialMediaPost.get_an_to_post()
            if adoption_notice is not None:
                logging.info(f"Posting adoption notice: {adoption_notice} ({adoption_notice.id})")
                try:
                    post = post_an_to_fedi(adoption_notice)
                    context = {"action_was_posting": True, "post": post, "posted_successfully": True}
                except requests.exceptions.ConnectionError as e:
                    logging.error(f"Could not post fediverse post: {e}")
                    context = {"action_was_posting": True,
                               "posted_successfully": False,
                               "error_message": _("Verbindungsfehler. Vermittlung wurde nicht gepostet")}
                except requests.exceptions.HTTPError as e:
                    logging.error(f"Could not post fediverse post: {e}")
                    context = {"action_was_posting": True,
                               "posted_successfully": False,
                               "error_message": _("Fehler beim Posten. Vermittlung wurde nicht gepostet. Das kann "
                                                  "z.B. an falschen Zugangsdaten liegen. Kontaktieren einen Admin.")}
            else:
                context = {"action_was_posting": True,
                           "posted_successfully": False,
                           "error_message": _("Keine Vermittlung zum Posten gefunden.")}
    return render(request, 'fellchensammlung/mod-tool-overview.html', context=context)


def deactivate_an(request, adoption_notice_id):
    adoption_notice = get_object_or_404(AdoptionNotice, pk=adoption_notice_id)
    if request.method == "POST":
        reason_for_closing = request.POST.get("reason_for_closing")
        adoption_notice.set_closed(reason_for_closing)
        return redirect(reverse("adoption-notice-detail", args=[adoption_notice.pk], ))
    context = {"adoption_notice": adoption_notice, }
    return render(request, 'fellchensammlung/misc/deactivate-an.html', context=context)
