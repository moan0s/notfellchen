import logging

from .geo import GeoAPI
from ..forms import AdoptionNoticeSearchForm
from ..models import SearchSubscription, AdoptionNotice, BaseNotification, SexChoicesWithAll, Location


def notify_search_subscribers(new_adoption_notice: AdoptionNotice):
    for search_subscription in SearchSubscription.objects.all():
        BaseNotification.objects.create(user=search_subscription.owner)


class Search():
    def __init__(self):
        self.sex = None
        self.area_search = None
        self.max_distance = None
        self.location_string = None
        self.search_position = None
        self.location = None
        self.place_not_found = False  # Indicates that a location was given but could not be geocoded
        self.search_form = None

    def __eq__(self, other):
        """
        Custom equals that also supports SearchSubscriptions
        """
        return self.location.name == other.location.name and self.sex == other.sex and self.max_distance == other.max_distance

    def _locate(self):
        if self.location is None:
            self.location = Location.get_location_from_string(self.location_string)

    def get_adoption_notices(self):
        adoptions = AdoptionNotice.objects.order_by("-created_at")
        adoptions = [adoption for adoption in adoptions if adoption.is_active]
        if self.sex is not None and self.sex != SexChoicesWithAll.ALL:
            adoptions = [adoption for adoption in adoptions if self.sex in adoption.sexes]
        if self.area_search and not self.place_not_found:
            adoptions = [a for a in adoptions if a.in_distance(self.search_position, self.max_distance)]

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
