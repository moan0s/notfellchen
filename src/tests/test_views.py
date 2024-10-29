from django.test import TestCase
from django.contrib.auth.models import Permission
from django.urls import reverse

from model_bakery import baker

from fellchensammlung.models import Animal, Species, AdoptionNotice, User, Location


class AnimalAndAdoptionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user0 = User.objects.create_user(username='testuser0',
                                              first_name="Admin",
                                              last_name="BOFH",
                                              password='12345')

        test_user1 = User.objects.create_user(username='testuser1',
                                              first_name="Max",
                                              last_name="Müller",
                                              password='12345')
        test_user1.save()

        adoption1 = baker.make(AdoptionNotice, name="TestAdoption1")
        rat = baker.make(Species, name="Farbratte")

        rat1 = baker.make(Animal,
                          name="Rat1",
                          adoption_notice=adoption1,
                          species=rat,
                          description="Eine unglaublich süße Ratte")

    def test_detail_animal(self):
        self.client.login(username='testuser0', password='12345')

        response = self.client.post(reverse('animal-detail', args="1"))
        self.assertEqual(response.status_code, 200)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser0')
        self.assertContains(response, "Rat1")

    def test_detail_animal_notice(self):
        self.client.login(username='testuser0', password='12345')

        response = self.client.post(reverse('adoption-notice-detail', args="1"))
        self.assertEqual(response.status_code, 200)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser0')
        self.assertContains(response, "TestAdoption1")
        self.assertContains(response, "Rat1")


class SearchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user0 = User.objects.create_user(username='testuser0',
                                              first_name="Admin",
                                              last_name="BOFH",
                                              password='12345')
        test_user0.save()

        # Location of Berlin: lat 52.5170365 lon 13.3888599 PLZ 10115 (Mitte)

        adoption1 = baker.make(AdoptionNotice, name="TestAdoption1")
        adoption2 = baker.make(AdoptionNotice, name="TestAdoption2")
        adoption3 = baker.make(AdoptionNotice, name="TestAdoption3")

        berlin = Location.get_location_from_string("Berlin")
        adoption1.location = berlin
        adoption1.save()
        stuttgart = Location.get_location_from_string("Tübingen")
        adoption3.location = stuttgart
        adoption3.save()

        adoption1.set_active()
        adoption3.set_active()
        adoption2.set_to_review()

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

    def test_plz_search(self):
        response = self.client.post(reverse('search'), {"max_distance": 100, "location": "Berlin"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestAdoption1")
        self.assertNotContains(response, "TestAdoption3")
