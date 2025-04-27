import logging
from django.utils.translation import gettext_lazy as _

from .geo import LocationProxy, Position
from ..forms import AdoptionNoticeSearchForm
from ..models import SearchSubscription, AdoptionNotice, AdoptionNoticeNotification, SexChoicesWithAll, Location


def notify_search_subscribers(adoption_notice: AdoptionNotice, only_if_active: bool = True):
    """
    This functions checks for all search subscriptions if the new adoption notice fits the search.
    If the new adoption notice fits the search subscription, it sends a notification to the user that created the search.
    """
    logging.debug(f"Notifying {adoption_notice}.")
    if only_if_active and not adoption_notice.is_active:
        logging.debug(f"No notifications triggered for adoption notice {adoption_notice} because it's not active.")
        return
    for search_subscription in SearchSubscription.objects.all():
        logging.debug(f"Search subscription {search_subscription} found.")
        search = Search(search_subscription=search_subscription)
        if search.adoption_notice_fits_search(adoption_notice):
            notification_text = f"{_('Zu deiner Suche')} {search_subscription} wurde eine neue Vermittlung gefunden"
            AdoptionNoticeNotification.objects.create(user=search_subscription.owner,
                                                      title=f"{_('Neue Vermittlung')}: {adoption_notice}",
                                                      adoption_notice=adoption_notice,
                                                      text=notification_text)
            logging.debug(f"Notification for search subscription {search_subscription} was sent.")
        else:
            logging.debug(f"Adoption notice {adoption_notice} was not fitting the search subscription.")

    logging.info(f"Subscribers for AN {adoption_notice.pk} have been notified\n")


class Search:
    def __init__(self, request=None, search_subscription=None):
        self.sex = None
        self.area_search = None
        self.max_distance = None
        self.location = None  # Can either be Location (DjangoModel) or LocationProxy
        self.place_not_found = False  # Indicates that a location was given but could not be geocoded
        self.search_form = None
        # Either place_id or location string must be set for area search
        self.location_string = None

        if request:
            self.search_from_request(request)
        elif search_subscription:
            self.search_from_search_subscription(search_subscription)

    def __str__(self):
        return f"Search: {self.sex=}, {self.location=}, {self.area_search=}, {self.max_distance=}"

    def __eq__(self, other):
        """
        Custom equals that also supports SearchSubscriptions

        Only allowed to be called for located subscriptions
        """
        # If both locations are empty check only for sex
        if self.location is None and other.location is None:
            return self.sex == other.sex
        # If one location is empty and the other is not, they are not equal
        elif self.location is not None and other.location is None or self.location is None and other.location is not None:
            return False
        return self.location == other.location and self.sex == other.sex and self.max_distance == other.max_distance

    def _locate(self):
        try:
            self.location = LocationProxy(self.location_string)
        except ValueError:
            self.place_not_found = True

    @property
    def position(self):
        if self.area_search and not self.place_not_found:
            return Position(latitude=self.location.latitude, longitude=self.location.longitude)
        else:
            return None

    def adoption_notice_fits_search(self, adoption_notice: AdoptionNotice):
        # Make sure sex is set and sex is not set to all (then it can be disregarded)
        if self.sex is not None and self.sex != SexChoicesWithAll.ALL:
            # AN does not fit search if search sex is not in available sexes of this AN
            if not self.sex in adoption_notice.sexes:
                logging.debug("Sex mismatch")
                return False
        # make sure it's an area search and the place is found to check location
        if self.area_search and not self.place_not_found:
            # If adoption notice is in not in search distance, return false
            if not adoption_notice.in_distance(self.location.position, self.max_distance):
                logging.debug("Area mismatch")
                return False
        return True

    def get_adoption_notices(self):
        adoptions = AdoptionNotice.objects.order_by("-created_at")
        # Filter for active adoption notices
        adoptions = [adoption for adoption in adoptions if adoption.is_active]
        # Check if adoption notice fits search.
        adoptions = [adoption for adoption in adoptions if self.adoption_notice_fits_search(adoption)]

        return adoptions

    def search_from_request(self, request):
        if request.method == 'POST':
            self.search_form = AdoptionNoticeSearchForm(request.POST)
            self.search_form.is_valid()
            self.sex = self.search_form.cleaned_data["sex"]

            if self.search_form.cleaned_data["location_string"] != "" and self.search_form.cleaned_data[
                "max_distance"] != "":
                self.area_search = True
                self.location_string = self.search_form.cleaned_data["location_string"]
                self.max_distance = int(self.search_form.cleaned_data["max_distance"])
                self._locate()
        else:
            self.search_form = AdoptionNoticeSearchForm()

    def search_from_predefined_i_location(self, i_location, max_distance=100):
        self.sex = SexChoicesWithAll.ALL
        self.location = i_location.location
        self.area_search = True
        self.search_form = AdoptionNoticeSearchForm(initial={"location_string": self.location.name,
                                                             "max_distance": max_distance,
                                                             "sex": SexChoicesWithAll.ALL})
        self.max_distance = max_distance

    def search_from_search_subscription(self, search_subscription: SearchSubscription):
        self.sex = search_subscription.sex
        self.location = search_subscription.location
        self.area_search = True
        self.max_distance = search_subscription.max_distance

    def subscribe(self, user):
        logging.info(f"{user} subscribed to search")
        if isinstance(self.location, LocationProxy):
            self.location = Location.get_location_from_proxy(self.location)
        SearchSubscription.objects.create(owner=user,
                                          location=self.location,
                                          sex=self.sex,
                                          max_distance=self.max_distance)

    def get_subscription_or_none(self, user):
        user_subscriptions = SearchSubscription.objects.filter(owner=user)
        for subscription in user_subscriptions:
            if self == subscription:
                return subscription

    def is_subscribed(self, user):
        """
        Returns true if a user is already subscribed to a search with these parameters
        """
        subscription = self.get_subscription_or_none()
        if subscription is None:
            return False
        else:
            return True
