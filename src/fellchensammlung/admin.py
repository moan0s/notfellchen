from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Animal, Species, RescueOrganization, AdoptionNotice, Location, Rule, Image, ModerationAction, Report, Member


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
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Animal)
admin.site.register(Species)
admin.site.register(RescueOrganization)
admin.site.register(Location)
admin.site.register(AdoptionNotice)
admin.site.register(Rule)
admin.site.register(Image)
admin.site.register(Report)
admin.site.register(ModerationAction)
