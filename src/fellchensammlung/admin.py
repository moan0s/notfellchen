from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django.utils.html import format_html

from .models import User, Language, Text, ReportComment, ReportAdoptionNotice, Log, Timestamp

from .models import Animal, Species, RescueOrganization, AdoptionNotice, Location, Rule, Image, ModerationAction, \
    Comment, Report, Announcement, AdoptionNoticeStatus, User, Subscriptions


class StatusInline(admin.StackedInline):
    model = AdoptionNoticeStatus


@admin.register(AdoptionNotice)
class AdoptionNoticeAdmin(admin.ModelAdmin):
    search_fields = ("name__contains", "description__contains")
    inlines = [
        StatusInline,
    ]


# Re-register UserAdmin
admin.site.register(User)


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


@admin.register(RescueOrganization)
class RescueOrganizationAdmin(admin.ModelAdmin):
    search_fields = ("name__contains", )
    list_display = ("name", "trusted", "allows_using_materials", "website")
    list_filter = ("allows_using_materials", "trusted",)


admin.site.register(Animal)
admin.site.register(Species)
admin.site.register(Location)
admin.site.register(Rule)
admin.site.register(Image)
admin.site.register(ModerationAction)
admin.site.register(Language)
admin.site.register(Text)
admin.site.register(Announcement)
admin.site.register(AdoptionNoticeStatus)
admin.site.register(Subscriptions)
admin.site.register(Log)
admin.site.register(Timestamp)
