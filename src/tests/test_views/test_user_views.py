from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from model_bakery import baker

from fellchensammlung.models import AdoptionNotice, User, TrustLevel, Notification


class UserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user0 = User.objects.create_user(username='testuser0',
                                                  first_name="Admin",
                                                  last_name="BOFH",
                                                  password='12345')
        cls.test_user0.trust_level = TrustLevel.ADMIN
        cls.test_user0.save()

        cls.test_user1 = User.objects.create_user(username='testuser1',
                                                  first_name="Max",
                                                  last_name="Müller",
                                                  password='12345')

        cls.test_user2 = User.objects.create_user(username='testuser2',
                                                  first_name="Mira",
                                                  last_name="Müller",
                                                  password='12345')

        adoption1 = baker.make(AdoptionNotice, name="TestAdoption1", owner=cls.test_user0)
        notification1 = baker.make(Notification,
                                   title="TestNotification1",
                                   user_to_notify=cls.test_user0,
                                   adoption_notice=adoption1)
        notification2 = baker.make(Notification, title="TestNotification1", user_to_notify=cls.test_user1)
        notification3 = baker.make(Notification, title="TestNotification1", user_to_notify=cls.test_user2)
        token = baker.make(Token, user=cls.test_user0)

    def test_detail_self(self):
        self.client.login(username='testuser1', password='12345')

        response = self.client.post(reverse('user-me'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Max")

    def test_detail_self_via_id(self):
        self.client.login(username='testuser1', password='12345')

        response = self.client.post(reverse('user-detail', args=str(self.test_user1.pk)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Max")

    def test_detail_admin_with_token(self):
        self.client.login(username='testuser0', password='12345')

        response = self.client.post(reverse('user-me'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Token.objects.get(user=self.test_user0).key)

    def test_detail_unauthenticated(self):
        response = self.client.get(reverse('user-me'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/user/me/")

    def test_detail_unauthorized(self):
        self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('user-detail', args=str(self.test_user1.pk)))
        self.assertEqual(response.status_code, 403)

    def test_detail_authorized(self):
        self.client.login(username='testuser0', password='12345')
        response = self.client.get(reverse('user-detail', args=str(self.test_user1.pk)))
        self.assertEqual(response.status_code, 200)
