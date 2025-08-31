from time import sleep

from django.test import TestCase
from django.urls import reverse
from fellchensammlung.models import SearchSubscription, User, TrustLevel, AdoptionNotice, Location, SexChoicesWithAll, \
    Animal, Species, SexChoices, Notification
from model_bakery import baker

from fellchensammlung.tools.geo import LocationProxy
from fellchensammlung.tools.model_helpers import NotificationTypeChoices, AdoptionNoticeStatusChoices
from fellchensammlung.tools.search import AdoptionNoticeSearch, notify_search_subscribers


class TestSearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user0 = User.objects.create_user(username='testuser0',
                                                  first_name="Admin",
                                                  last_name="BOFH",
                                                  password='12345')

        cls.test_user1 = User.objects.create_user(username='testuser1',
                                                  first_name="Max",
                                                  last_name="Müller",
                                                  password='12345')
        cls.test_user2 = User.objects.create_user(username='testuser2',
                                                  first_name="Miriam",
                                                  last_name="Müller",
                                                  password='12345')
        cls.test_user0.trust_level = TrustLevel.ADMIN
        cls.test_user0.save()

        rat = baker.make(Species, name="Farbratte")

        cls.location_stuttgart = Location.get_location_from_string("Stuttgart")

        cls.location_tue = Location.get_location_from_string("Kirchentellinsfurt")
        cls.location_berlin = Location.get_location_from_string("Berlin")

        cls.adoption1 = baker.make(AdoptionNotice, name="TestAdoption1", owner=cls.test_user0,
                                   location=cls.location_stuttgart)
        rat1 = baker.make(Animal,
                          name="Rat1",
                          adoption_notice=cls.adoption1,
                          species=rat,
                          sex=SexChoices.MALE,
                          description="Eine unglaublich süße Ratte")
        cls.adoption1.adoption_notice_status = AdoptionNoticeStatusChoices.Active.SEARCHING

        cls.adoption2 = baker.make(AdoptionNotice, name="TestAdoption2", owner=cls.test_user0, location=cls.location_berlin)
        rat2 = baker.make(Animal,
                          name="Rat2",
                          adoption_notice=cls.adoption2,
                          species=rat,
                          sex=SexChoices.FEMALE,
                          description="Eine unglaublich süße Ratte")
        cls.adoption2.adoption_notice_status = AdoptionNoticeStatusChoices.Active.SEARCHING

        cls.subscription1 = SearchSubscription.objects.create(owner=cls.test_user1,
                                                              location=cls.location_tue,
                                                              max_distance=50,
                                                              sex=SexChoicesWithAll.MALE)

        cls.subscription2 = SearchSubscription.objects.create(owner=cls.test_user2,
                                                              location=cls.location_berlin,
                                                              max_distance=50,
                                                              sex=SexChoicesWithAll.ALL)

    def test_equals(self):
        search_subscription1 = SearchSubscription.objects.create(owner=self.test_user0,
                                                                 location=self.location_stuttgart,
                                                                 sex=SexChoicesWithAll.ALL,
                                                                 max_distance=100
                                                                 )
        search1 = AdoptionNoticeSearch()
        search1.search_position = LocationProxy("Stuttgart").position
        search1.max_distance = 100
        search1.area_search = True
        search1.sex = SexChoicesWithAll.ALL
        search1.location_string = "Stuttgart"
        search1._locate()

        self.assertEqual(search_subscription1, search1)

    def test_adoption_notice_fits_search(self):
        search1 = AdoptionNoticeSearch(search_subscription=self.subscription1)
        self.assertTrue(search1.adoption_notice_fits_search(self.adoption1))
        self.assertFalse(search1.adoption_notice_fits_search(self.adoption2))

        search2 = AdoptionNoticeSearch(search_subscription=self.subscription2)
        self.assertFalse(search2.adoption_notice_fits_search(self.adoption1))
        self.assertTrue(search2.adoption_notice_fits_search(self.adoption2))

    def test_notification(self):
        """
        Simulates as if a new adoption notice is added and checks if Notifications are triggered.

        Must simulate adding a new adoption notice, the actual celery task can not be tested as celery can not
        be tested as it can't access the in-memory test database.
        https://stackoverflow.com/questions/46530784/make-django-test-case-database-visible-to-celery/46564964#46564964
        """
        notify_search_subscribers(self.adoption1)

        self.assertTrue(Notification.objects.filter(user_to_notify=self.test_user1,
                                                    adoption_notice=self.adoption1,
                                                    notification_type=NotificationTypeChoices.AN_FOR_SEARCH_FOUND).exists())
        self.assertFalse(Notification.objects.filter(user_to_notify=self.test_user2,).exists())
