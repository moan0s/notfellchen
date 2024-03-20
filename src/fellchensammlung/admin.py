from django.contrib import admin

from django.contrib import admin

from .models import Animal, Species, RescueOrganization, AdoptionNotice, Location, Rule

admin.site.register(Animal)
admin.site.register(Species)
admin.site.register(RescueOrganization)
admin.site.register(Location)
admin.site.register(AdoptionNotice)
admin.site.register(Rule)