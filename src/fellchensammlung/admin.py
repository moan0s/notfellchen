from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django.utils.html import format_html

from .models import User, Language, Text, ReportComment, ReportAdoptionNotice

from .models import Animal, Species, RescueOrganization, AdoptionNotice, Location, Rule, Image, ModerationAction, \
    Member, Comment, Report, Announcement


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class MemberInline(admin.StackedInline):
    model = Member
    can_delete = False
    verbose_name_plural = "member"


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [MemberInline]


# Re-register UserAdmin
admin.site.register(User, UserAdmin)


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


admin.site.register(Animal)
admin.site.register(Species)
admin.site.register(RescueOrganization)
admin.site.register(Location)
admin.site.register(AdoptionNotice)
admin.site.register(Rule)
admin.site.register(Image)
admin.site.register(ModerationAction)
admin.site.register(Language)
admin.site.register(Text)
admin.site.register(Announcement)
