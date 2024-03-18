from django.contrib import admin

from django.contrib import admin

from .models import Animal, Species, RescueOrganization, AdoptionNotice, Location

admin.site.register(Animal)
admin.site.register(Species)
admin.site.register(RescueOrganization)
admin.site.register(Location)
admin.site.register(AdoptionNotice)