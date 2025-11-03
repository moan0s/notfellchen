import uuid
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import base64

from .tools import misc, geo
from notfellchen.settings import MEDIA_URL, base_url
from .tools.geo import LocationProxy, Position
from .tools.misc import time_since_as_hr_string
from .tools.model_helpers import NotificationTypeChoices, AdoptionNoticeStatusChoices, AdoptionProcess, \
    AdoptionNoticeStatusChoicesDescriptions, RegularCheckStatusChoices, reason_for_signup_label, \
    reason_for_signup_help_text
from .tools.model_helpers import ndm as NotificationDisplayMapping


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            help_text=_("Der Name einer natürliche Sprache wie Deutsch, Englisch oder Arabisch."),
                            unique=True)

    languagecode = models.CharField(max_length=10,
                                    # Translators: This helptext includes an URL
                                    help_text=_(
                                        "Der standartisierte Sprachcode. Mehr Informationen: http://www.i18nguy.com/unicode/language-identifiers.html"),
                                    verbose_name=_('Sprachcode'))

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name

    class Meta:
        verbose_name = _('Sprache')
        verbose_name_plural = _('Sprachen')


class Location(models.Model):
    place_id = models.CharField(max_length=200)  # OSM id
    latitude = models.FloatField(verbose_name=_("Breitengrad"))
    longitude = models.FloatField(verbose_name=_("Längengrad"))
    name = models.CharField(max_length=2000)
    city = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Stadt'))
    housenumber = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Hausnummer"))
    postcode = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Postleitzahl"))
    street = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Straße"))
    county = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Landkreis"))
    # Country code as per ISO 3166-1 alpha-2
    # https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
    countrycode = models.CharField(max_length=2, verbose_name=_("Ländercode"),
                                   help_text=_("Standardisierter Ländercode nach ISO 3166-1 ALPHA-2"),
                                   blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Standort")
        verbose_name_plural = _("Standorte")

    def __str__(self):
        if self.city and self.postcode:
            return f"{self.city} ({self.postcode})"
        else:
            return f"{self.name}"

    @property
    def position(self):
        return (self.latitude, self.longitude)

    @staticmethod
    def get_location_from_string(location_string):
        try:
            proxy = LocationProxy(location_string)
        except ValueError:
            return None
        location = Location.get_location_from_proxy(proxy)
        return location

    @staticmethod
    def get_location_from_proxy(proxy):
        location = Location.objects.create(
            place_id=proxy.place_id,
            latitude=proxy.latitude,
            longitude=proxy.longitude,
            name=proxy.name,
            postcode=proxy.postcode,
            city=proxy.city,
            street=proxy.street,
            county=proxy.county,
            countrycode=proxy.countrycode,
        )
        return location

    @staticmethod
    def add_location_to_object(instance):
        """Search the location given in the location string and add it to the object"""
        location = Location.get_location_from_string(instance.location_string)
        instance.location = location
        instance.save()


class ImportantLocation(models.Model):
    class Meta:
        verbose_name = _("Wichtiger Standort")
        verbose_name_plural = _("Wichtige Standorte")

    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse('search-by-location', kwargs={'important_location_slug': self.slug})


class ExternalSourceChoices(models.TextChoices):
    OSM = "OSM", _("Open Street Map")


class AllowUseOfMaterialsChices(models.TextChoices):
    USE_MATERIALS_ALLOWED = "allowed", _("Usage allowed")
    USE_MATERIALS_REQUESTED = "requested", _("Usage requested")
    USE_MATERIALS_DENIED = "denied", _("Usage denied")
    USE_MATERIALS_OTHER = "other", _("It's complicated")
    USE_MATERIALS_NOT_ASKED = "not_asked", _("Not asked")


class Species(models.Model):
    """Model representing a species of animal."""
    name = models.CharField(max_length=200, help_text=_('Name der Tierart'),
                            verbose_name=_('Name'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.name

    class Meta:
        verbose_name = _('Tierart')
        verbose_name_plural = _('Tierarten')


class RescueOrganization(models.Model):
    name = models.CharField(max_length=200)
    trusted = models.BooleanField(default=False, verbose_name=_('Vertrauenswürdig'))
    allows_using_materials = models.CharField(max_length=200,
                                              default=AllowUseOfMaterialsChices.USE_MATERIALS_NOT_ASKED,
                                              choices=AllowUseOfMaterialsChices.choices,
                                              verbose_name=_('Erlaubt Nutzung von Inhalten'))
    location_string = models.CharField(max_length=200, verbose_name=_("Ort der Organisation"), null=True, blank=True, )
    location = models.ForeignKey(Location, on_delete=models.PROTECT, blank=True, null=True)
    instagram = models.URLField(null=True, blank=True, verbose_name=_('Instagram Profil'))
    facebook = models.URLField(null=True, blank=True, verbose_name=_('Facebook Profil'))
    fediverse_profile = models.URLField(null=True, blank=True, verbose_name=_('Fediverse Profil'))
    email = models.EmailField(null=True, blank=True, verbose_name=_('E-Mail'))
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Telefonnummer'))
    website = models.URLField(null=True, blank=True, verbose_name=_('Website'))
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(auto_now_add=True, verbose_name=_('Datum der letzten Prüfung'))
    internal_comment = models.TextField(verbose_name=_("Interner Kommentar"), null=True, blank=True, )
    description = models.TextField(null=True, blank=True, verbose_name=_('Beschreibung'))  # Markdown allowed
    external_object_identifier = models.CharField(max_length=200, null=True, blank=True,
                                                  verbose_name=_('External Object Identifier'))
    external_source_identifier = models.CharField(max_length=200, null=True, blank=True,
                                                  choices=ExternalSourceChoices.choices,
                                                  verbose_name=_('External Source Identifier'))
    exclude_from_check = models.BooleanField(default=False, verbose_name=_('Von Prüfung ausschließen'),
                                             help_text=_("Organisation von der manuellen Überprüfung ausschließen, "
                                                         "z.B. weil Tiere nicht online geführt werden"))
    regular_check_status = models.CharField(max_length=30, choices=RegularCheckStatusChoices.choices,
                                            default=RegularCheckStatusChoices.REGULAR_CHECK,
                                            verbose_name=_('Status der regelmäßigen Prüfung'),
                                            help_text=_(
                                                "Organisationen können, durch ändern dieser Einstellung, von der "
                                                "regelmäßigen Prüfung ausgeschlossen werden."))
    ongoing_communication = models.BooleanField(default=False, verbose_name=_('In aktiver Kommunikation'),
                                                help_text=_(
                                                    "Es findet gerade Kommunikation zwischen Notfellchen und der Organisation statt."))
    parent_org = models.ForeignKey("RescueOrganization", on_delete=models.PROTECT, blank=True, null=True)
    # allows to specify if a rescue organization has a specialization for dedicated species
    specializations = models.ManyToManyField(Species, blank=True)
    twenty_id = models.UUIDField(verbose_name=_("Twenty-ID"), null=True, blank=True,
                                 help_text=_("ID der der Organisation in Twenty"))

    class Meta:
        unique_together = ('external_object_identifier', 'external_source_identifier',)
        ordering = ['name']
        verbose_name = _("Tierschutzorganisation")
        verbose_name_plural = _("Tierschutzorganisationen")

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        super().clean()
        if self.location is None and self.location_string is None:
            raise ValidationError(_('Location or Location String must be set'))

    def get_absolute_url(self):
        return reverse("rescue-organization-detail", args=[str(self.pk)])

    @property
    def adoption_notices(self):
        return AdoptionNotice.objects.filter(organization=self)

    @property
    def adoption_notices_in_hierarchy(self):
        """
        Shows all adoption notices of this rescue organization and all child organizations.
        """
        adoption_notices_discovered = list(self.adoption_notices)
        if self.child_organizations:
            for child in self.child_organizations:
                adoption_notices_discovered.extend(child.adoption_notices_in_hierarchy)
        return adoption_notices_discovered

    @property
    def adoption_notices_in_hierarchy_divided_by_status(self):
        """Returns two lists of adoption notices, the first active, the other inactive."""
        active_adoption_notices = []
        inactive_adoption_notices = []
        for an in self.adoption_notices_in_hierarchy:
            if an.is_active:
                active_adoption_notices.append(an)
            else:
                inactive_adoption_notices.append(an)
        return active_adoption_notices, inactive_adoption_notices

    @property
    def position(self):
        if self.location:
            return Position(latitude=self.location.latitude, longitude=self.location.longitude)
        else:
            return None

    @property
    def description_short(self):
        if self.description is None:
            return ""
        if len(self.description) > 200:
            return self.description[:200] + _(f" ... [weiterlesen]({self.get_absolute_url()})")
        else:
            return self.description

    def set_checked(self):
        self.last_checked = timezone.now()
        self.save()

    @property
    def last_checked_hr(self):
        time_since_last_checked = timezone.now() - self.last_checked
        return time_since_as_hr_string(time_since_last_checked)

    @property
    def species_urls(self):
        return SpeciesSpecificURL.objects.filter(rescue_organization=self)

    @property
    def has_contact_data(self):
        """
        Returns true if at least one type of contact data is available.
        """
        return self.instagram or self.facebook or self.website or self.phone_number or self.email or self.fediverse_profile

    @property
    def child_organizations(self):
        return RescueOrganization.objects.filter(parent_org=self)

    def in_distance(self, position, max_distance, unknown_true=True):
        """
        Returns a boolean indicating if the Location of the adoption notice is within a given distance to the position

        If the location is none, we by default return that the location is within the given distance
        """
        return geo.object_in_distance(self, position, max_distance, unknown_true)


# Admins can perform all actions and have the highest trust associated with them
# Moderators can make moderation decisions regarding the deletion of content
# Coordinators can create adoption notices without them being checked
# Members can create adoption notices that must be activated
class TrustLevel(models.IntegerChoices):
    MEMBER = 1, 'Member'
    COORDINATOR = 2, 'Coordinator'
    MODERATOR = 3, 'Moderator'
    ADMIN = 4, 'Admin'


class User(AbstractUser):
    """
    Model that holds a user's profile, including the django user model

    The trust levels act as permission system and can be displayed as a badge for the user
    """

    trust_level = models.IntegerField(
        choices=TrustLevel.choices,
        default=TrustLevel.MEMBER,  # Default to the lowest trust level
    )
    preferred_language = models.ForeignKey(Language, on_delete=models.PROTECT, null=True, blank=True,
                                           verbose_name=_('Bevorzugte Sprache'))
    updated_at = models.DateTimeField(auto_now=True)
    organization_affiliation = models.ForeignKey(RescueOrganization, on_delete=models.PROTECT, null=True, blank=True,
                                                 verbose_name=_('Organisation'))
    reason_for_signup = models.TextField(verbose_name=reason_for_signup_label, help_text=reason_for_signup_help_text)
    email_notifications = models.BooleanField(verbose_name=_("Benachrichtigung per E-Mail"), default=True)
    REQUIRED_FIELDS = ["reason_for_signup", "email"]

    class Meta:
        verbose_name = _('Nutzer*in')
        verbose_name_plural = _('Nutzer*innen')

    def get_full_name(self):
        if self.first_name and self.last_name:
            return self.first_name + self.last_name
        else:
            return self.username

    def get_absolute_url(self):
        return reverse("user-detail", args=[str(self.pk)])

    def get_full_url(self):
        return f"{base_url}{self.get_absolute_url()}"

    def get_notifications_url(self):
        return self.get_absolute_url()

    def get_unread_notifications(self):
        return Notification.objects.filter(user_to_notify=self, read=False)

    def get_num_unread_notifications(self):
        return Notification.objects.filter(user_to_notify=self, read=False).count()

    @property
    def adoption_notices(self):
        return AdoptionNotice.objects.filter(owner=self)

    @property
    def owner(self):
        return self


class Image(models.Model):
    image = models.ImageField(upload_to='images', verbose_name=_("Bild"), help_text=_("Wähle ein Bild aus"))
    alt_text = models.TextField(max_length=2000, verbose_name=_('Alternativtext'),
                                help_text=_("Beschreibe das Bild für blinde und sehbehinderte Menschen"))
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.alt_text

    class Meta:
        verbose_name = _("Bild")
        verbose_name_plural = _("Bilder")

    @property
    def as_html(self):
        return f'<img src="{MEDIA_URL}/{self.image}" alt="{self.alt_text}">'

    @property
    def as_base64(self):
        encoded_string = base64.b64encode(self.image.file.read())
        return encoded_string.decode("utf-8")


class AdoptionNotice(models.Model):
    class Meta:
        permissions = [
            ("create_active_adoption_notice", "Can create an active adoption notice"),
        ]
        verbose_name = _("Vermittlung")
        verbose_name_plural = _("Vermittlungen")

    def __str__(self):
        return self.name

    created_at = models.DateField(verbose_name=_('Erstellt am'), default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_checked = models.DateTimeField(verbose_name=_('Zuletzt überprüft am'), default=timezone.now)
    searching_since = models.DateField(verbose_name=_('Sucht nach einem Zuhause seit'))
    name = models.CharField(max_length=200, verbose_name=_('Titel der Vermittlung'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Beschreibung'))
    organization = models.ForeignKey(RescueOrganization, blank=True, null=True, on_delete=models.SET_NULL,
                                     verbose_name=_('Organisation'))
    further_information = models.URLField(null=True, blank=True,
                                          verbose_name=_('Link zu mehr Informationen'),
                                          help_text=_(
                                              "Verlinke hier die Quelle der Vermittlung (z.B. die Website des "
                                              "Tierheims)"))
    group_only = models.BooleanField(default=False, verbose_name=_('Ausschließlich Gruppenadoption'))
    photos = models.ManyToManyField(Image, blank=True)
    location_string = models.CharField(max_length=200, verbose_name=_("Ortsangabe"))
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL, )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Creator'))
    adoption_notice_status = models.TextField(max_length=64, verbose_name=_('Status'),
                                              choices=AdoptionNoticeStatusChoices.all_choices())
    adoption_process = models.TextField(null=True, blank=True,
                                        max_length=64, verbose_name=_('Adoptionsprozess'),
                                        choices=AdoptionProcess)

    @property
    def animals(self):
        return Animal.objects.filter(adoption_notice=self)

    @property
    def sexes(self):
        sexes = set()
        for animal in self.animals:
            sexes.add(animal.sex)
        return sexes

    @property
    def num_per_sex(self):
        print(f"{self.pk} x")
        num_per_sex = dict()
        for sex in SexChoices:
            num_per_sex[sex] = len([animal for animal in self.animals if animal.sex == sex])
        return num_per_sex

    @property
    def species(self):
        species = set()
        for animal in self.animals:
            species.add(animal.species)
        return species

    @property
    def last_checked_hr(self):
        time_since_last_checked = timezone.now() - self.last_checked
        return time_since_as_hr_string(time_since_last_checked)

    def sex_code(self):
        # Treat Intersex as mixed in order to increase their visibility
        if len(self.sexes) > 1:
            return "mixed"

        sex = self.sexes.pop()
        if sex == SexChoices.MALE:
            return "male"
        elif sex == SexChoices.FEMALE:
            return "female"
        else:
            return "mixed"

    @property
    def comments(self):
        return Comment.objects.filter(adoption_notice=self)

    @property
    def position(self):
        if self.location is None:
            return None
        else:
            return self.location.latitude, self.location.longitude

    def _get_short_description(self, length: int) -> str:
        if self.description is None:
            return ""
        elif len(self.description) > length:
            return self.description[:length] + f" ... [weiterlesen]({self.get_absolute_url()})"
        else:
            return self.description

    @property
    def description_short(self):
        return self._get_short_description(200)

    @property
    def description_100_short(self):
        return self._get_short_description(90)

    def get_absolute_url(self):
        """Returns the url to access a detailed page for the adoption notice."""
        return reverse('adoption-notice-detail', args=[str(self.id)])

    def get_full_url(self):
        """Returns the url including protocol and domain"""
        return f"{base_url}{self.get_absolute_url()}"

    def get_report_url(self):
        """Returns the url to report an adoption notice."""
        return reverse('report-adoption-notice', args=[str(self.id)])

    def get_subscriptions(self):
        # returns all subscriptions to that adoption notice
        return Subscriptions.objects.filter(adoption_notice=self)

    @staticmethod
    def get_active_ANs():
        active_ans = [an for an in AdoptionNotice.objects.all() if an.is_active]
        return active_ans

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

    def in_distance(self, position, max_distance, unknown_true=True):
        """
        Returns a boolean indicating if the Location of the adoption notice is within a given distance to the position

        If the location is none, we by default return that the location is within the given distance
        """
        return geo.object_in_distance(self, position, max_distance, unknown_true)

    @staticmethod
    def _values_of(list_of_enums):
        return list(map(lambda x: x[0], list_of_enums))

    @property
    def is_active(self):
        return self.adoption_notice_status in self._values_of(AdoptionNoticeStatusChoices.Active.choices)

    @property
    def is_disabled(self):
        return self.adoption_notice_status in self._values_of(AdoptionNoticeStatusChoices.Disabled.choices)

    @property
    def is_closed(self):
        return self.adoption_notice_status in self._values_of(AdoptionNoticeStatusChoices.Closed.choices)

    @property
    def is_awaiting_action(self):
        return self.adoption_notice_status in self._values_of(AdoptionNoticeStatusChoices.AwaitingAction.choices)

    @property
    def status_description(self):
        return AdoptionNoticeStatusChoicesDescriptions.mapping[self.adoption_notice_status]

    def set_unchecked(self):
        self.last_checked = timezone.now()
        self.adoption_notice_status = AdoptionNoticeStatusChoices.AwaitingAction.UNCHECKED
        self.save()

        for subscription in self.get_subscriptions():
            notification_title = _("Vermittlung deaktiviert:") + f" {self.name}"
            text = _("Die folgende Vermittlung wurde deaktiviert: ") + f"[{self.name}]({self.get_absolute_url()})"
            Notification.objects.create(user_to_notify=subscription.owner,
                                        notification_type=NotificationTypeChoices.AN_WAS_DEACTIVATED,
                                        adoption_notice=self,
                                        text=text,
                                        title=notification_title)

    def last_posted(self, platform=None):
        if platform is None:
            last_post = SocialMediaPost.objects.filter(adoption_notice=self).order_by('-created_at').first()
        else:
            last_post = SocialMediaPost.objects.filter(adoption_notice=self, platform=platform).order_by(
                '-created_at').first()
        return last_post.created_at


class SexChoices(models.TextChoices):
    FEMALE = "F", _("Weiblich")
    MALE = "M", _("Männlich")
    MALE_NEUTERED = "M_N", _("Männlich, kastriert")
    FEMALE_NEUTERED = "F_N", _("Weiblich, kastriert")
    INTER = "I", _("Intergeschlechtlich")


class SexChoicesWithAll(models.TextChoices):
    FEMALE = "F", _("Weiblich")
    MALE = "M", _("Männlich")
    MALE_NEUTERED = "M_N", _("Männlich, kastriert")
    FEMALE_NEUTERED = "F_N", _("Weiblich Kastriert")
    INTER = "I", _("Intergeschlechtlich")
    ALL = "A", _("Alle")


class Animal(models.Model):
    class Meta:
        verbose_name = _('Tier')
        verbose_name_plural = _('Tiere')

    date_of_birth = models.DateField(verbose_name=_('Geburtsdatum'))
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Beschreibung'))
    species = models.ForeignKey(Species, on_delete=models.PROTECT, verbose_name=_("Tierart"))
    photos = models.ManyToManyField(Image, blank=True, verbose_name=_("Fotos"))
    sex = models.CharField(
        max_length=20,
        choices=SexChoices.choices,
        verbose_name=_("Geschlecht")
    )
    adoption_notice = models.ForeignKey(AdoptionNotice, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

    @property
    def age(self):
        return timezone.now().today().date() - self.date_of_birth

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


class DistanceChoices(models.IntegerChoices):
    TWENTY = 20, '20 km'
    FIFTY = 50, '50 km'
    ONE_HUNDRED = 100, '100 km'
    TWO_HUNDRED = 200, '200 km'
    FIVE_HUNDRED = 500, '500 km'


class SearchSubscription(models.Model):
    """
    SearchSubscriptions allow a user to get a notification when a new AdoptionNotice is added that matches their Search
    criteria. Search criteria are location, SexChoicesWithAll and distance

    Process:
    - User performs a normal search
    - User clicks Button "Subscribe to this Search"
    - SearchSubscription is added to database
    - On new AdoptionNotice: Check all existing SearchSubscriptions for matches
    - For matches: Send notification to user of the SearchSubscription
    """

    class Meta:
        verbose_name = _("Abonnierte Suche")
        verbose_name_plural = _("Abonnierte Suchen")

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True)
    sex = models.CharField(max_length=20, choices=SexChoicesWithAll.choices, verbose_name=_("Geschlecht"))
    max_distance = models.IntegerField(choices=DistanceChoices.choices, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Zuletzt geändert am"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Erstellt am"))

    def __str__(self):
        if self.location and self.max_distance:
            return f"{self.owner}: [{SexChoicesWithAll(self.sex).label}] {self.max_distance}km - {self.location}"
        else:
            return f"{self.owner}: [{SexChoicesWithAll(self.sex).label}]"


class Rule(models.Model):
    """
    Class to store rules
    """

    class Meta:
        verbose_name = _("Regel")
        verbose_name_plural = _("Regeln")

    title = models.CharField(max_length=200)

    # Markdown is allowed in rule text
    rule_text = models.TextField(verbose_name=_("Regeltext"))
    language = models.ForeignKey(Language, on_delete=models.PROTECT, verbose_name=_("Sprache"))
    # Rule identifier allows to translate rules with the same identifier
    rule_identifier = models.CharField(max_length=24,
                                       verbose_name=_("Regel-ID"),
                                       help_text=_("Ein eindeutiger Identifikator der Regel. Ein Regelobjekt "
                                                   "derselben Regel in einer anderen Sprache muss den gleichen "
                                                   "Identifikator haben"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Zuletzt geändert am"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Erstellt am"))

    def __str__(self):
        return self.title


class Report(models.Model):
    class Meta:
        verbose_name = _("Meldung")
        verbose_name_plural = _("Meldungen")

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
    reported_broken_rules = models.ManyToManyField(Rule, verbose_name=_("Regeln gegen die verstoßen wurde"))
    user_comment = models.TextField(blank=True, verbose_name=_("Kommentar/Zusätzliche Information"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Zuletzt geändert am"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Erstellt am"))

    def __str__(self):
        return f"[{self.status}]: {self.user_comment:.20}"

    def get_absolute_url(self):
        """Returns the url to access a detailed page for the report."""
        return reverse('report-detail', args=[str(self.id)])

    def get_full_url(self):
        return f"{base_url}{self.get_absolute_url()}"

    def get_reported_rules(self):
        return self.reported_broken_rules.all()

    def get_moderation_actions(self):
        return ModerationAction.objects.filter(report=self)

    @property
    def reported_content(self):
        """
        Dynamically fetch the reported content based on subclass.
        The alternative would be to use the ContentType framework:
        https://docs.djangoproject.com/en/5.1/ref/contrib/contenttypes/
        """
        if hasattr(self, "reportadoptionnotice"):
            return self.reportadoptionnotice.adoption_notice
        elif hasattr(self, "reportcomment"):
            return self.reportcomment.reported_comment
        return None

    @property
    def reported_content_url(self):
        """
        Same as reported_content, just for url
        """
        if hasattr(self, "reportadoptionnotice"):
            print(self.reportadoptionnotice.adoption_notice.get_absolute_url)
            return self.reportadoptionnotice.adoption_notice.get_absolute_url
        elif hasattr(self, "reportcomment"):
            return self.reportcomment.reported_comment.get_absolute_url
        return None


class ReportAdoptionNotice(Report):
    adoption_notice = models.ForeignKey("AdoptionNotice", on_delete=models.CASCADE)

    @property
    def reported_content(self):
        return self.adoption_notice

    def __str__(self):
        return f"Report der Vermittlung {self.adoption_notice}"


class ReportComment(Report):
    reported_comment = models.ForeignKey("Comment", on_delete=models.CASCADE)

    @property
    def reported_content(self):
        return self.reported_comment


class ModerationAction(models.Model):
    class Meta:
        verbose_name = _("Moderationsaktion")
        verbose_name_plural = _("Moderationsaktionen")

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
    updated_at = models.DateTimeField(auto_now=True)
    public_comment = models.TextField(blank=True)
    # Only visible to moderator
    private_comment = models.TextField(blank=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    def __str__(self):
        return f"[{self.action}]: {self.public_comment}"


class TextTypeChoices(models.TextChoices):
    DEDICATED = "dedicated", _("Fest zugeordnet")
    MALE = "M", _("Männlich")
    MALE_NEUTERED = "M_N", _("Männlich, kastriert")
    FEMALE_NEUTERED = "F_N", _("Weiblich, kastriert")
    INTER = "I", _("Intergeschlechtlich")


class Text(models.Model):
    """
    Base class to store markdown content
    """
    title = models.CharField(max_length=100, verbose_name=_("Titel"))
    content = models.TextField(verbose_name="Inhalt")
    language = models.ForeignKey(Language, verbose_name="Sprache", on_delete=models.PROTECT)
    text_code = models.CharField(max_length=24, verbose_name="Text code", blank=True)

    class Meta:
        verbose_name = "Text"
        verbose_name_plural = "Texte"

    def __str__(self):
        return f"{self.title} ({self.language})"

    @staticmethod
    def get_texts(text_codes, language, expandable_dict=None):
        if expandable_dict is None:
            expandable_dict = {}
        for text_code in text_codes:
            try:
                expandable_dict[text_code] = Text.objects.get(text_code=text_code, language=language, )
            except Text.DoesNotExist:
                expandable_dict[text_code] = None
        return expandable_dict


class Announcement(Text):
    """
    Class to store announcements that should be displayed for all users
    """

    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banner")

    logged_in_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publish_start_time = models.DateTimeField(verbose_name="Veröffentlichungszeitpunkt")
    publish_end_time = models.DateTimeField(verbose_name="Veröffentlichungsende")
    IMPORTANT = "important"
    WARNING = "warning"
    INFO = "info"
    TYPES = {
        IMPORTANT: "important",
        WARNING: "warning",
        INFO: "info",
    }
    type = models.CharField(choices=TYPES, max_length=100, default=INFO)

    @property
    def is_active(self):
        return self.publish_start_time < timezone.now() < self.publish_end_time

    def __str__(self):
        return f"[{'🟢' if self.is_active else '🔴'}]{self.title} ({self.language})"

    @staticmethod
    def get_active_announcements(logged_in=False, language=None):
        if logged_in:
            all_active_announcements = [a for a in Announcement.objects.all() if a.is_active]
        else:
            all_active_announcements = [a for a in Announcement.objects.filter(logged_in_only=False) if a.is_active]
        if language is None:
            return all_active_announcements
        else:
            if logged_in:
                announcements_in_language = Announcement.objects.filter(language=language)
            else:
                announcements_in_language = Announcement.objects.filter(language=language, logged_in_only=False)
            active_announcements_in_language = [a for a in announcements_in_language if a.is_active]

            untranslated_announcements = []
            text_codes = [announcement.text_code for announcement in active_announcements_in_language]
            for announcement in all_active_announcements:
                if announcement.language != language and announcement.text_code not in text_codes:
                    untranslated_announcements.append(announcement)
            return active_announcements_in_language + untranslated_announcements


class Comment(models.Model):
    """
    Class to store comments in markdown content
    """

    class Meta:
        verbose_name = _("Kommentar")
        verbose_name_plural = _("Kommentare")

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Nutzer*in'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    adoption_notice = models.ForeignKey(AdoptionNotice, on_delete=models.CASCADE, verbose_name=_('Vermittlung'))
    text = models.TextField(verbose_name="Inhalt")
    reply_to = models.ForeignKey("self", verbose_name="Antwort auf", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} at {self.created_at.strftime('%H:%M %d.%m.%y')}: {self.text:.10}"

    def get_report_url(self):
        return reverse('report-comment', args=[str(self.id)])

    @property
    def get_absolute_url(self):
        return self.adoption_notice.get_absolute_url()


class Notification(models.Model):
    class Meta:
        verbose_name = _("Benachrichtigung")
        verbose_name_plural = _("Benachrichtigungen")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notification_type = models.CharField(max_length=200,
                                         choices=NotificationTypeChoices.choices,
                                         verbose_name=_('Benachrichtigungsgrund'))
    user_to_notify = models.ForeignKey(User,
                                       on_delete=models.CASCADE,
                                       verbose_name=_('Empfänger*in'),
                                       help_text=_("Useraccount der benachrichtigt wird"),
                                       related_name='user')
    title = models.CharField(max_length=100, verbose_name=_("Titel"))
    text = models.TextField(verbose_name="Inhalt")
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Gelesen am"))
    comment = models.ForeignKey(Comment, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Antwort'))
    adoption_notice = models.ForeignKey(AdoptionNotice, blank=True, null=True, on_delete=models.CASCADE,
                                        verbose_name=_('Vermittlung'))
    user_related = models.ForeignKey(User,
                                     blank=True, null=True,
                                     on_delete=models.CASCADE, verbose_name=_('Verwandter Useraccount'),
                                     help_text=_("Useraccount auf den sich die Benachrichtigung bezieht."))
    report = models.ForeignKey(Report,
                               blank=True, null=True,
                               on_delete=models.CASCADE,
                               verbose_name=_('Report'),
                               help_text=_("Report auf den sich die Benachrichtigung bezieht."))

    def __str__(self):
        return f"[{self.user_to_notify}] {self.title} ({self.created_at})"

    def get_absolute_url(self):
        self.user_to_notify.get_notifications_url()

    def mark_read(self):
        self.read = True
        self.read_at = timezone.now()
        self.save()

    def get_body_part(self):
        return NotificationDisplayMapping[self.notification_type].web_partial


class Subscriptions(models.Model):
    """Subscription to a AdoptionNotice"""

    class Meta:
        verbose_name = _("Abonnement")
        verbose_name_plural = _("Abonnements")

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Nutzer*in'))
    adoption_notice = models.ForeignKey(AdoptionNotice, on_delete=models.CASCADE, verbose_name=_('Vermittlung'),
                                        help_text=_("Vermittlung die abonniert wurde"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner} - {self.adoption_notice}"


class Log(models.Model):
    """
    Basic class that allows logging random entries for later inspection
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Nutzer*in"), blank=True, null=True)
    action = models.CharField(max_length=255, verbose_name=_("Aktion"))
    text = models.CharField(max_length=1000, verbose_name=_("Log text"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.action}] - {self.user} - {self.created_at.strftime('%H:%M:%S %d-%m-%Y ')}"


class Timestamp(models.Model):
    """
    Class to store timestamps based on keys
    """

    class Meta:
        verbose_name = _("Zeitstempel")
        verbose_name_plural = _("Zeitstempel")

    key = models.CharField(max_length=255, verbose_name=_("Schlüssel"), primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Zeitstempel"))
    data = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return f"[{self.key}] - {self.timestamp.strftime('%H:%M:%S %d-%m-%Y ')} - {self.data}"


class SpeciesSpecificURL(models.Model):
    """
    Model that allows to specify a URL for a rescue organization where a certain species can be found
    """

    class Meta:
        verbose_name = _("Tierartspezifische URL")
        verbose_name_plural = _("Tierartspezifische URLs")

    species = models.ForeignKey(Species, on_delete=models.CASCADE, verbose_name=_("Tierart"))
    rescue_organization = models.ForeignKey(RescueOrganization, on_delete=models.CASCADE,
                                            verbose_name=_("Tierschutzorganisation"))
    url = models.URLField(verbose_name=_("Tierartspezifische URL"))


class PlatformChoices(models.TextChoices):
    FEDIVERSE = "fediverse", _("Fediverse")


class SocialMediaPost(models.Model):
    created_at = models.DateField(verbose_name=_('Erstellt am'), default=timezone.now)
    platform = models.CharField(max_length=255, verbose_name=_("Social Media Platform"),
                                choices=PlatformChoices.choices)
    adoption_notice = models.ForeignKey(AdoptionNotice, on_delete=models.CASCADE, verbose_name=_('Vermittlung'))
    url = models.URLField(verbose_name=_("URL"))

    @staticmethod
    def get_an_to_post():
        adoption_notices_without_post = AdoptionNotice.objects.filter(socialmediapost__isnull=True,
                                                                      adoption_notice_status__in=AdoptionNoticeStatusChoices.Active.values)
        return adoption_notices_without_post.first()

    def __str__(self):
        return f"{self.platform} - {self.adoption_notice}"
