from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from datetime import datetime

from fellchensammlung.tools import misc


class Image(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images')
    alt_text = models.TextField(max_length=2000)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


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


class AdoptionNotice(models.Model):
    def __str__(self):
        return f"{self.name}"

    created_at = models.DateField(verbose_name=_('Created at'), default=datetime.now)
    searching_since = models.DateField(verbose_name=_('Searching for a home since'))
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    organization = models.ForeignKey(RescueOrganization, blank=True, null=True, on_delete=models.SET_NULL,
                                     verbose_name=_('Organization'))
    further_information = models.URLField(null=True, blank=True, verbose_name=_('Link to further information'))
    group_only = models.BooleanField(default=False, verbose_name=_('Only group adoption'))
    photos = models.ManyToManyField(Image, blank=True)

    @property
    def animals_list(self):
        return self.animals.all()

    def get_absolute_url(self):
        """Returns the url to access a detailed page for the animal."""
        return reverse('adoption-notice-detail', args=[str(self.id)])


class Animal(models.Model):
    MALE_NEUTERED = "M_N"
    MALE = "M"
    FEMALE_NEUTERED = "F_N"
    FEMALE = "F"
    SEX_CHOICES = {
        MALE_NEUTERED: "male_neutered",
        MALE: "male",
        FEMALE_NEUTERED: "female_neutered",
        FEMALE: "female",
    }

    date_of_birth = models.DateField(verbose_name=_('Date of birth'))
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    species = models.ForeignKey(Species, on_delete=models.PROTECT)
    photos = models.ManyToManyField(Image, blank=True)
    sex = models.CharField(max_length=20, choices=SEX_CHOICES, )
    adoption_notice = models.ForeignKey(AdoptionNotice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    @property
    def age(self):
        return datetime.today().date() - self.date_of_birth

    @property
    def hr_age(self):
        """Returns a human-readable age based on the date of birth."""
        return misc.age_as_hr_string(self.age)

    def get_absolute_url(self):
        """Returns the url to access a detailed page for the animal."""
        return reverse('animal-detail', args=[str(self.id)])


class MarkdownContent(models.Model):
    """
    Base class to store markdown content
    """
    title = models.CharField(max_length=100)
    content = models.TextField()

    class Meta:
        verbose_name_plural = "Markdown content"

    def __str__(self):
        return self.title
