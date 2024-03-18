from django.db import models
from django.utils.translation import gettext_lazy as _


class Species(models.Model):
    """Model representing a species of animal."""
    name = models.CharField(max_length=200, help_text=_('Enter a animal species'),
                            verbose_name=_('Name'))

    def __str__(self):
        """String for representing the Model object."""
        return self.name

    class Meta:
        verbose_name = _('Species')
        verbose_name_plural = _('Species')


class Location(models.Model):
    def __str__(self):
        return f"{self.name}"

    GERMANY = "DE"
    AUSTRIA = "AT"
    SWITZERLAND = "CH"
    COUNTRIES_CHOICES = {
        GERMANY: "Germany",
        AUSTRIA: "Austria",
        SWITZERLAND: "Switzerland"
    }

    name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    country = models.CharField(max_length=20, choices=COUNTRIES_CHOICES)
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))


class RescueOrganization(models.Model):
    def __str__(self):
        return f"{self.name}"

    name = models.CharField(max_length=200)
    trusted = models.BooleanField(default=False, verbose_name=_('Trusted'))
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    instagram = models.URLField(null=True, blank=True, verbose_name=_('Instagram profile'))
    facebook = models.URLField(null=True, blank=True, verbose_name=_('Facebook profile'))
    fediverse_profile = models.URLField(null=True, blank=True, verbose_name=_('Fediverse profile'))
    website = models.URLField(null=True, blank=True, verbose_name=_('Website'))



class Animal(models.Model):
    def __str__(self):
        return f"{self.name}"

    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('Date of birth'))
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    species = models.ForeignKey(Species, on_delete=models.PROTECT)

class AdoptionNotice(models.Model):
    def __str__(self):
        return f"{self.name}"

    created_at = models.DateField(verbose_name=_('Created at'))
    searching_since = models.DateField(verbose_name=_('Searching for a home since'))
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    organization = models.ForeignKey(RescueOrganization, blank=True, null=True, on_delete=models.SET_NULL,
                                     verbose_name=_('Organization'))
    further_information = models.URLField(null=True, blank=True, verbose_name=_('Link to further information'))
    group_only = models.BooleanField(default=False, verbose_name=_('Only group adoption'))
    animals = models.ManyToManyField(Animal)

