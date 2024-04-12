import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.contrib.auth.models import AbstractUser

from fellchensammlung.tools import misc


class Image(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images')
    alt_text = models.TextField(max_length=2000)

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
    class Meta:
        permissions = [
            ("create_active_adoption_notice", "Can create an active adoption notice"),
        ]

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
    def animals(self):
        return Animal.objects.filter(adoption_notice=self)

    def get_absolute_url(self):
        """Returns the url to access a detailed page for the animal."""
        return reverse('adoption-notice-detail', args=[str(self.id)])

    def get_report_url(self):
        return reverse('report-adoption-notice', args=[str(self.id)])

    def get_photos(self):
        """
        First trys to get group photos that are attached to the adoption notice if there is none it trys to fetch
        them from the animals
        """
        group_photos = self.photos.all()
        if len(group_photos) > 0:
            return group_photos
        else:
            photos = []
            for animal in self.animals:
                photos.extend(animal.photos.all())
            if len(photos) > 0:
                return photos

    def get_photo(self):
        """
        Returns the first photo it finds.
        First trys to get group photos that are attached to the adoption notice if there is none it trys to fetch
        them from the animals
        """
        group_photos = self.photos.all()
        if len(group_photos) > 0:
            return group_photos[0]
        else:
            photos = []
            for animal in self.animals:
                photos.extend(animal.photos.all())
            if len(photos) > 0:
                return photos[0]


class Animal(models.Model):
    MALE_NEUTERED = "M_N"
    MALE = "M"
    FEMALE_NEUTERED = "F_N"
    FEMALE = "F"
    SEX_CHOICES = {
        MALE_NEUTERED: "neutered male",
        MALE: "male",
        FEMALE_NEUTERED: "neutered female",
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

    def get_photo(self):
        """
        Selects a random photo from the animal
        """
        photos = self.photos.all()
        if len(photos) > 0:
            return photos[0]

    def get_photos(self):
        """
        Selects all photos from the animal
        """
        return self.photos.all()

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


class Rule(models.Model):
    """
    Class to store rules
    """
    title = models.CharField(max_length=200)

    # Markdown is allowed in rule text
    rule_text = models.TextField()

    def __str__(self):
        return self.title


class Report(models.Model):
    class Meta:
        permissions = []

    ACTION_TAKEN = "action taken"
    NO_ACTION_TAKEN = "no action taken"
    WAITING = "waiting"
    STATES = {
        ACTION_TAKEN: "Action was taken",
        NO_ACTION_TAKEN: "No action was taken",
        WAITING: "Waiting for moderator action",
    }
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text=_('ID dieses reports'),
                          verbose_name=_('ID'))
    status = models.CharField(max_length=30, choices=STATES)
    reported_broken_rules = models.ManyToManyField(Rule, blank=True)
    adoption_notice = models.ForeignKey("AdoptionNotice", on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.status}]: {self.adoption_notice.name}"

    def get_absolute_url(self):
        """Returns the url to access a detailed page for the report."""
        return reverse('report-detail', args=[str(self.id)])

    def get_reported_rules(self):
        return self.reported_broken_rules.all()

    def get_moderation_actions(self):
        return ModerationAction.objects.filter(report=self)


class ModerationAction(models.Model):
    BAN = "user_banned"
    DELETE = "content_deleted"
    COMMENT = "comment"
    OTHER = "other_action_taken"
    NONE = "no_action_taken"
    ACTIONS = {
        BAN: "User was banned",
        DELETE: "Content was deleted",
        COMMENT: "Comment was added",
        OTHER: "Other action was taken",
        NONE: "No action was taken"
    }
    action = models.CharField(max_length=30, choices=ACTIONS.items())
    created_at = models.DateTimeField(auto_now_add=True)
    public_comment = models.TextField(blank=True)
    # Only visible to moderator
    private_comment = models.TextField(blank=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    # TODO: Needs field for moderator that performed the action

    def __str__(self):
        return f"[{self.action}]: {self.public_comment}"


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            help_text=_("Enter a natural languages name (e.g. English, French, Japanese etc.)."),
                            unique=True)

    languagecode = models.CharField(max_length=10,
                                    # Translators: This helptext includes an URL
                                    help_text=_(
                                        "Enter the language code for this language. For further information see  http://www.i18nguy.com/unicode/language-identifiers.html"),
                                    verbose_name=_('Language code'))

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name

    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')


"""
Membership
"""


class User(AbstractUser):
    pass


class Member(models.Model):
    """
    Model that holds a user's profile, including the django user model

    It is created upon creation of a new django user (see add_member)
    The trust levels act as permission system and can be displayed as a badge for the user
    """

    # Admins can perform all actions and have the highest trust associated with them
    # Moderators can make moderation decisions regarding the deletion of content
    # Coordinators can create adoption notices without them being checked
    # Members can create adoption notices that must be activated
    ADMIN = "admin"
    MODERATOR = "Moderator"
    COORDINATOR = "Koordinator*in"
    MEMBER = "Mitglied"
    TRUES_LEVEL = {
        ADMIN: "Administrator*in",
        MODERATOR: "Moderator*in",
        COORDINATOR: "Koordinator*in",
        MEMBER: "Mitglied",
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User'))
    preferred_language = models.ForeignKey(Language, on_delete=models.PROTECT, null=True, blank=True,
                                           verbose_name=_('Preferred language'))
    trust_level = models.CharField(choices=TRUES_LEVEL, max_length=100, default=MEMBER)

    class Meta:
        verbose_name = _('Member')
        verbose_name_plural = _('Members')

    @receiver(post_save, sender=User)
    def add_member(sender, instance, created, raw, using, **kwargs):
        if len(Member.objects.filter(user=instance)) != 1:
            Member.objects.create(user=instance)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse("member-detail", args=[str(self.user.id)])
