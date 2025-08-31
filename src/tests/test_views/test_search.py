from django.test import TestCase
from django.contrib.auth.models import Permission
from django.urls import reverse

from model_bakery import baker

from fellchensammlung.models import AdoptionNotice, User, Location, SearchSubscription
from fellchensammlung.tools.model_helpers import AdoptionNoticeStatusChoices


class SearchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user0 = User.objects.create_user(username='testuser0',
                                              first_name="Max",
                                              last_name="BOFH",
                                              password='12345')
        test_user0.save()

        test_user1 = User.objects.create_user(username='testuser1',
                                              first_name="Moritz",
                                              last_name="BOFH",
                                              password='12345')
        test_user1.save()

        # Location of Berlin: lat 52.5170365 lon 13.3888599 PLZ 10115 (Mitte)

        adoption1 = baker.make(AdoptionNotice, name="TestAdoption1",
                               adoption_notice_status=AdoptionNoticeStatusChoices.Active.SEARCHING)
        adoption2 = baker.make(AdoptionNotice, name="TestAdoption2")
        adoption3 = baker.make(AdoptionNotice, name="TestAdoption3",
                               adoption_notice_status=AdoptionNoticeStatusChoices.Active.INTERESTED)

        berlin = Location.get_location_from_string("Berlin")
        adoption1.location = berlin
        adoption1.save()

        stuttgart = Location.get_location_from_string("Stuttgart")
        adoption3.location = stuttgart
        adoption3.save()

        adoption2.set_unchecked()

        cls.subscription1 = SearchSubscription.objects.create(owner=test_user1,
                                                              max_distance=200,
                                                              location=stuttgart,
                                                              sex="A")

    def test_basic_view(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "TestAdoption1")
        self.assertNotContains(response, "TestAdoption2")
        self.assertContains(response, "TestAdoption3")

    def test_basic_view_logged_in(self):
        self.client.login(username='testuser0', password='12345')
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser0')

        self.assertContains(response, "TestAdoption1")
        self.assertContains(response, "TestAdoption3")
        self.assertNotContains(response, "TestAdoption2")

    def test_unauthenticated_subscribe(self):
        response = self.client.post(reverse('search'), {"subscribe_to_search": ""})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/suchen/")

    def test_unauthenticated_unsubscribe(self):
        response = self.client.post(reverse('search'), {"unsubscribe_to_search": 1})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/suchen/")

    def test_unauthorized_unsubscribe(self):
        self.client.login(username='testuser0', password='12345')
        # This should not be allowed as the subscription owner is different than the request user
        response = self.client.post(reverse('search'), {"unsubscribe_to_search": self.subscription1.id})
        self.assertEqual(response.status_code, 403)

    def test_subscribe(self):
        self.client.login(username='testuser0', password='12345')
        response = self.client.post(reverse('search'), {"max_distance": 50, "location_string": "Berlin", "sex": "A",
                                                        "subscribe_to_search": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SearchSubscription.objects.filter(owner=User.objects.get(username='testuser0'),
                                                          max_distance=50).exists())

    def test_unsubscribe(self):
        user0 = User.objects.get(username='testuser0')
        self.client.login(username='testuser0', password='12345')
        location = Location.get_location_from_string("München")
        subscription = SearchSubscription.objects.create(owner=user0, max_distance=200, location=location, sex="A")
        response = self.client.post(reverse('search'), {"max_distance": 200, "location_string": "München", "sex": "A",
                                                        "unsubscribe_to_search": subscription.pk})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SearchSubscription.objects.filter(owner=User.objects.get(username='testuser0'),
                                                           max_distance=200).exists())

    def test_location_search(self):
        response = self.client.post(reverse('search'), {"max_distance": 50, "location_string": "Berlin", "sex": "A"})
        self.assertEqual(response.status_code, 200)
        # We can't use assertContains because TestAdoption3 will always be in response at is included in map
        # In order to test properly, we need to only care for the context that influences the list display
        an_names = [a.name for a in response.context["adoption_notices"]]
        self.assertTrue("TestAdoption1" in an_names)  # Adoption in Berlin
        self.assertFalse("TestAdoption3" in an_names)  # Adoption in Stuttgart
