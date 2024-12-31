import logging
from django.utils.translation import gettext_lazy as _

from .geo import GeoAPI
from ..forms import AdoptionNoticeSearchForm
from ..models import SearchSubscription, AdoptionNotice, AdoptionNoticeNotification, SexChoicesWithAll, Location


def notify_search_subscribers(adoption_notice: AdoptionNotice):
    """
    This functions checks for all search subscriptions if the new adoption notice fits the search.
    If the new adoption notice fits the search subscription, it sends a notification to the user that created the search.
    """
    for search_subscription in SearchSubscription.objects.all():
        if search_subscription.adoption_notice_fits_search(adoption_notice):
            notification_text = f"{_('Zu deiner Suche')} {search_subscription} wurde eine neue Vermittlung gefunden"
            AdoptionNoticeNotification.objects.create(user=search_subscription.owner,
                                                      title=f"{_('Neue Vermittlung')}: {adoption_notice.title}",
                                                      adoption_notice=adoption_notice,
                                                      text=notification_text)


class Search:
    def __init__(self):
        self.sex = None
        self.area_search = None
        self.max_distance = None
        self.location_string = None
        self.search_position = None
        self.location = None
        self.place_not_found = False  # Indicates that a location was given but could not be geocoded
        self.search_form = None

    def __str__(self):
        return f"Search: {self.sex=}, {self.location=}, {self.search_position=}, {self.area_search=}, {self.max_distance=}"

    def __eq__(self, other):
        """
        Custom equals that also supports SearchSubscriptions

        Only allowed to be called for located subscriptions
        """
        return self.location.name == other.location.name and self.sex == other.sex and self.max_distance == other.max_distance

    def _locate(self):
        if self.location is None:
            self.location = Location.get_location_from_string(self.location_string)

    def adoption_notice_fits_search(self, adoption_notice: AdoptionNotice):
        # Make sure sex is set and sex is not set to all (then it can be disregarded)
        if self.sex is not None and self.sex != SexChoicesWithAll.ALL:
            # AN does not fit search if search sex is not in available sexes of this AN
            if not self.sex in adoption_notice.sexes:
                return False
        # make sure it's an area search and the place is found to check location
        if self.area_search and not self.place_not_found:
            # If adoption notice is in not in search distance, return false
            if not adoption_notice.in_distance(self.search_position, self.max_distance):
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

                geo_api = GeoAPI()
                self.search_position = geo_api.get_coordinates_from_query(self.location_string)
                if self.search_position is None:
                    self.place_not_found = True
        else:
            self.search_form = AdoptionNoticeSearchForm()

    @staticmethod
    def search_from_search_subscription(search_subscription: SearchSubscription):
        search = Search()
        search.sex = search_subscription.sex
        search.location = search_subscription.location
        search.search_position = (search_subscription.location.latitude, search_subscription.location.longitude)
        search.area_search = True
        search.max_distance = search_subscription.max_distance


        return search


    def subscribe(self, user):
        logging.info(f"{user} subscribed to search")
        self._locate()
        SearchSubscription.objects.create(owner=user,
                                          location=self.location,
                                          sex=self.sex,
                                          radius=self.max_distance)

    def is_subscribed(self, user):
        """
        Returns true if a user is already subscribed to a search with these parameters
        """
        user_subscriptions = SearchSubscription.objects.filter(owner=user)
        self._locate()
        for subscription in user_subscriptions:
            if self == subscription:
                return True
        return False
