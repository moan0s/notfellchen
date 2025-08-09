from django.test import TestCase
from model_bakery import baker

from fellchensammlung.models import User, TrustLevel, Species, Location, AdoptionNotice, Notification
from fellchensammlung.tools.model_helpers import NotificationTypeChoices
from fellchensammlung.tools.notifications import notify_of_AN_to_be_checked


class TestNotifications(TestCase):
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

        cls.adoption1 = baker.make(AdoptionNotice, name="TestAdoption1", owner=cls.test_user1, )
        cls.adoption1.set_unchecked()  # Could also emit notification

    def test_notify_of_AN_to_be_checked(self):
        notify_of_AN_to_be_checked(self.adoption1)
        self.assertTrue(Notification.objects.filter(user_to_notify=self.test_user0,
                                                    adoption_notice=self.adoption1,
                                                    notification_type=NotificationTypeChoices.AN_IS_TO_BE_CHECKED).exists())
        self.assertTrue(Notification.objects.filter(user_to_notify=self.test_user1,
                                                    adoption_notice=self.adoption1,
                                                    notification_type=NotificationTypeChoices.AN_IS_TO_BE_CHECKED).exists())
        self.assertFalse(Notification.objects.filter(user_to_notify=self.test_user2,
                                                     adoption_notice=self.adoption1,
                                                     notification_type=NotificationTypeChoices.AN_IS_TO_BE_CHECKED).exists())
