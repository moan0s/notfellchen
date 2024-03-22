from django.contrib import admin

from django.contrib import admin

from .models import Animal, Species, RescueOrganization, AdoptionNotice, Location, Rule, Image, ModerationAction, Report

admin.site.register(Animal)
admin.site.register(Species)
admin.site.register(RescueOrganization)
admin.site.register(Location)
admin.site.register(AdoptionNotice)
admin.site.register(Rule)
admin.site.register(Image)
admin.site.register(Report)
admin.site.register(ModerationAction)
