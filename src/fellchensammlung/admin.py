import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode

from .models import User, Language, Text, ReportComment, ReportAdoptionNotice, Log, Timestamp, SearchSubscription, \
    SpeciesSpecificURL, ImportantLocation

from .models import Animal, Species, RescueOrganization, AdoptionNotice, Location, Rule, Image, ModerationAction, \
    Comment, Report, Announcement, AdoptionNoticeStatus, User, Subscriptions, BaseNotification
from django.utils.translation import gettext_lazy as _


class StatusInline(admin.StackedInline):
    model = AdoptionNoticeStatus


@admin.register(AdoptionNotice)
class AdoptionNoticeAdmin(admin.ModelAdmin):
    search_fields = ("name__icontains", "description__icontains")
    list_filter = ("owner",)
    inlines = [
        StatusInline,
    ]
    actions = ("activate",)

    def activate(self, request, queryset):
        for obj in queryset:
            obj.set_active()

    activate.short_description = _("Ausgewählte Vermittlungen aktivieren")


# Re-register UserAdmin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("usernamname__icontains", "first_name__icontains", "last_name__icontains", "email__icontains")
    list_display = ("username", "email", "trust_level", "is_active", "view_adoption_notices")
    list_filter = ("is_active", "trust_level",)
    actions = ("export_as_csv",)

    def view_adoption_notices(self, obj):
        count = obj.adoption_notices.count()
        url = (
                reverse("admin:fellchensammlung_adoptionnotice_changelist")
                + "?"
                + urlencode({"owner__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Adoption Notices</a>', url, count)

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = _("Ausgewählte User exportieren")


def _reported_content_link(obj):
    reported_content = obj.reported_content
    return format_html(f'<a href="{reported_content.get_absolute_url}">{reported_content}</a>')


@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ["user_comment", "reported_content_link"]
    date_hierarchy = "created_at"

    def reported_content_link(self, obj):
        return _reported_content_link(obj)

    reported_content_link.short_description = "Reported Content"


@admin.register(ReportAdoptionNotice)
class ReportAdoptionNoticeAdmin(admin.ModelAdmin):
    list_display = ["user_comment", "reported_content_link"]
    date_hierarchy = "created_at"

    def reported_content_link(self, obj):
        return _reported_content_link(obj)

    reported_content_link.short_description = "Reported Content"


class SpeciesSpecificURLInline(admin.StackedInline):
    model = SpeciesSpecificURL


@admin.register(RescueOrganization)
class RescueOrganizationAdmin(admin.ModelAdmin):
    search_fields = ("name", "description", "internal_comment", "location_string")
    list_display = ("name", "trusted", "allows_using_materials", "website")
    list_filter = ("allows_using_materials", "trusted",)

    inlines = [
        SpeciesSpecificURLInline,
    ]


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    search_fields = ("title__icontains", "text_code__icontains",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_filter = ("user",)


@admin.register(BaseNotification)
class BaseNotificationAdmin(admin.ModelAdmin):
    list_filter = ("user", "read")


@admin.register(SearchSubscription)
class SearchSubscriptionAdmin(admin.ModelAdmin):
    list_filter = ("owner",)


class ImportantLocationInline(admin.StackedInline):
    model = ImportantLocation


class IsImportantListFilter(admin.SimpleListFilter):
    # See https://docs.djangoproject.com/en/5.1/ref/contrib/admin/filters/#modeladmin-list-filters
    title = _('Is Important Location?')

    parameter_name = 'important'

    def lookups(self, request, model_admin):
        return (
            ('is_important', _('Important Location')),
            ('is_normal', _('Normal Location')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'is_important':
            return queryset.filter(importantlocation__isnull=False)
        else:
            return queryset.filter(importantlocation__isnull=True)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ("name__icontains", "city__icontains")
    list_filter = [IsImportantListFilter]
    inlines = [
        ImportantLocationInline,
    ]


admin.site.register(Animal)
admin.site.register(Species)
admin.site.register(Rule)
admin.site.register(Image)
admin.site.register(ModerationAction)
admin.site.register(Language)
admin.site.register(Announcement)
admin.site.register(AdoptionNoticeStatus)
admin.site.register(Subscriptions)
admin.site.register(Log)
admin.site.register(Timestamp)
