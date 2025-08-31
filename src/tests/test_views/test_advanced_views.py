from django.test import TestCase
from django.urls import reverse

from model_bakery import baker

from fellchensammlung.models import Species, AdoptionNotice, User, Location, TrustLevel, \
    Animal, Subscriptions, Comment, Notification
from fellchensammlung.tools.model_helpers import NotificationTypeChoices, AdoptionNoticeStatusChoices


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

    def test_detail_adoption_notice(self):
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

        self.assertTrue(response.status_code < 400)
        self.assertTrue(AdoptionNotice.objects.get(name="TestAdoption4").is_active)
        an = AdoptionNotice.objects.get(name="TestAdoption4")
        animals = Animal.objects.filter(adoption_notice=an)
        self.assertTrue(len(animals) == 2)

    def test_creating_AN_as_user(self):
        self.client.login(username='testuser1', password='12345')

        form_data = {"name": "TestAdoption5",
                     "species": Species.objects.first().pk,
                     "num_animals": "3",
                     "date_of_birth": "2024-12-04",
                     "sex": "M",
                     "group_only": "on",
                     "searching_since": "2024-11-10",
                     "location_string": "München",
                     "description": "Blaaaa",
                     "further_information": "https://notfellchen.org/",
                     "save-and-add-another-animal": "Speichern"}

        response = self.client.post(reverse('add-adoption'), data=form_data)

        self.assertTrue(response.status_code < 400)
        self.assertFalse(AdoptionNotice.objects.get(name="TestAdoption5").is_active)
        an = AdoptionNotice.objects.get(name="TestAdoption5")
        animals = Animal.objects.filter(adoption_notice=an)
        self.assertTrue(len(animals) == 3)
        self.assertTrue(an.sexes == set("M", ))


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
        self.assertEqual(response.url, "/accounts/login/?next=/updatequeue/")

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
        self.assertTrue(self.adoption3.is_closed)


class AdoptionDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user0 = User.objects.create_user(username='testuser0',
                                              first_name="Admin",
                                              last_name="BOFH",
                                              password='12345')
        test_user0.save()

        cls.test_user1 = User.objects.create_user(username='testuser1',
                                                  first_name="Max",
                                                  last_name="Müller",
                                                  password='12345')
        test_user0.trust_level = TrustLevel.ADMIN
        test_user0.save()

        adoption1 = baker.make(AdoptionNotice, name="TestAdoption1")
        adoption2 = baker.make(AdoptionNotice, name="TestAdoption2")
        adoption3 = baker.make(AdoptionNotice, name="TestAdoption3")

        berlin = Location.get_location_from_string("Berlin")
        adoption1.location = berlin
        adoption1.save()

        stuttgart = Location.get_location_from_string("Stuttgart")
        adoption3.location = stuttgart
        adoption3.save()

        adoption1.adoption_notice_status = AdoptionNoticeStatusChoices.Active.SEARCHING
        adoption3.adoption_notice_status = AdoptionNoticeStatusChoices.Active.INTERESTED
        adoption2.set_unchecked()

    def test_basic_view(self):
        response = self.client.get(
            reverse('adoption-notice-detail', args=str(AdoptionNotice.objects.get(name="TestAdoption1").pk)), )
        self.assertEqual(response.status_code, 200)

    def test_basic_view_logged_in(self):
        self.client.login(username='testuser0', password='12345')
        response = self.client.get(
            reverse('adoption-notice-detail', args=str(AdoptionNotice.objects.get(name="TestAdoption1").pk)), )
        self.assertEqual(response.status_code, 200)

    def test_subscribe(self):
        self.client.login(username='testuser0', password='12345')
        response = self.client.post(
            reverse('adoption-notice-detail', args=str(AdoptionNotice.objects.get(name="TestAdoption1").pk)),
            data={"action": "subscribe"})
        self.assertTrue(Subscriptions.objects.filter(owner__username="testuser0").exists())

    def test_unsubscribe(self):
        # Make sure subscription exists
        an = AdoptionNotice.objects.get(name="TestAdoption1")
        user = User.objects.get(username="testuser0")
        subscription = Subscriptions.objects.get_or_create(owner=user, adoption_notice=an)

        # Unsubscribe
        self.client.login(username='testuser0', password='12345')
        response = self.client.post(
            reverse('adoption-notice-detail', args=str(an.pk)),
            data={"action": "unsubscribe"})
        self.assertFalse(Subscriptions.objects.filter(owner__username="testuser0").exists())

    def test_login_required(self):
        response = self.client.post(
            reverse('adoption-notice-detail', args=str(AdoptionNotice.objects.get(name="TestAdoption1").pk)),
            data={"action": "subscribe"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/vermittlung/1/")

    def test_unauthenticated_comment(self):
        response = self.client.post(
            reverse('adoption-notice-detail', args=str(AdoptionNotice.objects.get(name="TestAdoption1").pk)),
            data={"action": "comment"})
        self.assertEqual(response.status_code, 403)

    def test_comment(self):
        an1 = AdoptionNotice.objects.get(name="TestAdoption1")
        # Set up subscription
        Subscriptions.objects.create(owner=self.test_user1, adoption_notice=an1)
        self.client.login(username='testuser0', password='12345')
        response = self.client.post(
            reverse('adoption-notice-detail', args=str(an1.pk)),
            data={"action": "comment", "text": "Test"})
        self.assertTrue(Comment.objects.filter(user__username="testuser0").exists())
        self.assertFalse(Notification.objects.filter(user_to_notify__username="testuser0",
                                                     notification_type=NotificationTypeChoices.NEW_COMMENT).exists())
        self.assertTrue(Notification.objects.filter(user_to_notify__username="testuser1",
                                                    notification_type=NotificationTypeChoices.NEW_COMMENT).exists())


class AdoptionEditTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user0 = User.objects.create_user(username='testuser0',
                                              first_name="Admin",
                                              last_name="BOFH",
                                              password='12345')
        test_user0.save()

        cls.test_user1 = User.objects.create_user(username='testuser1',
                                                  first_name="Max",
                                                  last_name="Müller",
                                                  password='12345')

        adoption1 = baker.make(AdoptionNotice, name="TestAdoption1", description="Test1", owner=test_user0)
        adoption2 = baker.make(AdoptionNotice, name="TestAdoption2", description="Test2")

    def test_basic_view(self):
        response = self.client.get(
            reverse('adoption-notice-edit', args=str(AdoptionNotice.objects.get(name="TestAdoption1").pk)), )
        self.assertEqual(response.status_code, 302)

    def test_basic_view_logged_in_unauthorized(self):
        self.client.login(username='testuser1', password='12345')
        response = self.client.get(
            reverse('adoption-notice-edit', args=str(AdoptionNotice.objects.get(name="TestAdoption1").pk)), )
        self.assertEqual(response.status_code, 403)

    def test_basic_view_logged_in(self):
        self.client.login(username='testuser0', password='12345')
        response = self.client.get(
            reverse('adoption-notice-edit', args=str(AdoptionNotice.objects.get(name="TestAdoption1").pk)), )
        self.assertEqual(response.status_code, 200)

    def test_edit(self):
        data = {"name": "Mia",
                "searching_since": "01.01.2025",
                "location_string": "Paderborn",
                "organization": "",
                "description": "Test3",
                "further_information": ""}
        an = AdoptionNotice.objects.get(name="TestAdoption1")
        assert self.client.login(username='testuser0', password='12345')
        response = self.client.post(reverse("adoption-notice-edit", args=str(an.pk)), data=data, follow=True)
        self.assertEqual(response.redirect_chain[0][1],
                         302)  # See https://docs.djangoproject.com/en/5.1/topics/testing/tools/
        self.assertEqual(response.status_code, 200)  # Redirects to AN page
        self.assertContains(response, "Test3")
        self.assertContains(response, "Mia")
        self.assertNotContains(response, "Test1")
