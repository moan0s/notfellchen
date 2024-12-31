from django.test import TestCase
from django.contrib.auth.models import Permission
from django.urls import reverse

from model_bakery import baker

from fellchensammlung.models import Animal, Species, AdoptionNotice, User, Location, AdoptionNoticeStatus, TrustLevel
from fellchensammlung.views import add_adoption_notice


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
        test_user0.trust_level = TrustLevel.ADMIN
        test_user0.save()

        adoption1 = baker.make(AdoptionNotice, name="TestAdoption1", owner=test_user0)
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

    def test_creating_AN_as_admin(self):
        self.client.login(username='testuser0', password='12345')

        form_data = {"name": "TestAdoption4",
                     "species": Species.objects.first().pk,
                     "num_animals": "2",
                     "date_of_birth": "2024-11-04",
                     "sex": "M",
                     "group_only": "on",
                     "searching_since": "2024-11-10",
                     "location_string": "Mannheim",
                     "description": "Blaaaa",
                     "further_information": "https://notfellchen.org",
                     "save-and-add-another-animal": "Speichern"}

        response = self.client.post(reverse('add-adoption'), data=form_data)
        print(response.content)

        self.assertTrue(response.status_code < 400)
        self.assertTrue(AdoptionNotice.objects.get(name="TestAdoption4").is_active)



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
        adoption2.set_unchecked()

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
        response = self.client.post(reverse('search'), {"max_distance": 100, "location": "Berlin", "sex": "A"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestAdoption1")
        self.assertNotContains(response, "TestAdoption3")


class UpdateQueueTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user0 = User.objects.create_user(username='testuser0',
                                              first_name="Admin",
                                              last_name="BOFH",
                                              password='12345',
                                              trust_level=TrustLevel.MODERATOR)
        test_user0.is_superuser = True
        test_user0.save()

        # Location of Berlin: lat 52.5170365 lon 13.3888599 PLZ 10115 (Mitte)

        cls.adoption1 = baker.make(AdoptionNotice, name="TestAdoption1")
        adoption2 = baker.make(AdoptionNotice, name="TestAdoption2")
        cls.adoption3 = baker.make(AdoptionNotice, name="TestAdoption3")

        cls.adoption1.set_unchecked()
        cls.adoption3.set_unchecked()

    def test_login_required(self):
        response = self.client.get(reverse('updatequeue'))
        self.assertEqual(response.status_code, 302)
        self.assertEquals(response.url, "/accounts/login/?next=/updatequeue/")

    def test_set_updated(self):
        self.client.login(username='testuser0', password='12345')

        # First get the list
        response = self.client.get(reverse('updatequeue'))
        self.assertEqual(response.status_code, 200)
        # Make sure Adoption1 is in response
        self.assertContains(response, "TestAdoption1")
        self.assertNotContains(response, "TestAdoption2")

        self.assertFalse(self.adoption1.is_active)

        # Mark as checked
        response = self.client.post(reverse('updatequeue'), {"adoption_notice_id": self.adoption1.pk,
                                                             "action": "checked_active"})
        self.assertEqual(response.status_code, 200)
        self.adoption1.refresh_from_db()
        self.assertTrue(self.adoption1.is_active)

    def test_set_checked_inactive(self):
        self.client.login(username='testuser0', password='12345')
        # First get the list
        response = self.client.get(reverse('updatequeue'))
        self.assertEqual(response.status_code, 200)

        # Make sure Adoption3 is in response
        self.assertContains(response, "TestAdoption3")
        self.assertNotContains(response, "TestAdoption2")

        self.assertFalse(self.adoption3.is_active)

        # Mark as checked
        response = self.client.post(reverse('updatequeue'),
                                    {"adoption_notice_id": self.adoption3.id, "action": "checked_inactive"})
        self.assertEqual(response.status_code, 200)
        self.adoption3.refresh_from_db()

        # Make sure correct status is set and AN is not shown anymore
        self.assertNotContains(response, "TestAdoption3")
        self.assertFalse(self.adoption3.is_active)
        self.assertEqual(self.adoption3.adoptionnoticestatus.major_status, AdoptionNoticeStatus.CLOSED)

