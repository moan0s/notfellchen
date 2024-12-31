from django.test import TestCase
from fellchensammlung.models import SearchSubscription, User, TrustLevel, AdoptionNotice, Location, SexChoicesWithAll, \
    Animal, Species
from fellchensammlung.tools import search
from model_bakery import baker

from fellchensammlung.tools.geo import GeoAPI
from fellchensammlung.tools.search import Search


class TestSearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user0 = User.objects.create_user(username='testuser0',
                                              first_name="Admin",
                                              last_name="BOFH",
                                              password='12345')

        test_user1 = User.objects.create_user(username='testuser1',
                                              first_name="Max",
                                              last_name="Müller",
                                              password='12345')
        cls.test_user0.trust_level = TrustLevel.ADMIN
        cls.test_user0.save()

        adoption1 = baker.make(AdoptionNotice, name="TestAdoption1", owner=cls.test_user0)
        rat = baker.make(Species, name="Farbratte")

        rat1 = baker.make(Animal,
                          name="Rat1",
                          adoption_notice=adoption1,
                          species=rat,
                          description="Eine unglaublich süße Ratte")

        adoption2 = baker.make(AdoptionNotice, name="TestAdoption2", owner=cls.test_user0)
        cls.location = Location.get_location_from_string("Stuttgart")

    def test_equals(self):
        search_subscription1 = SearchSubscription.objects.create(owner=self.test_user0,
                                                                 location=self.location,
                                                                 sex=SexChoicesWithAll.ALL,
                                                                 max_distance=100
                                                                 )
        search1 = Search()
        geoapi = GeoAPI()
        search1.search_position = geoapi.get_coordinates_from_query("Stuttgart")
        search1.max_distance = 100
        search1.area_search = True
        search1.sex = SexChoicesWithAll.ALL
        search1.location_string = "Stuttgart"
        search1._locate()

        self.assertEqual(search_subscription1, search1)

