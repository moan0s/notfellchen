from datetime import datetime, timedelta
from django.utils import timezone

from django.test import TestCase
from model_bakery import baker

from fellchensammlung.models import Announcement, Language


class AnnouncementTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.language_de = baker.make(Language, name="Deutsch_", languagecode="de")
        cls.language_en = baker.make(Language, name="English_", languagecode="en")
        cls.announcement1 = baker.make(Announcement, title="Notfellchen reduziert um 1000%",
                                       content="Jetzt adoptieren was da ist!",
                                       publish_start_time=timezone.now() + timedelta(hours=-1),
                                       publish_end_time=timezone.now() + timedelta(hours=1),
                                       text_code="advert1",
                                       language=cls.language_de)
        cls.announcement2 = baker.make(Announcement, title="Notfellchen now on sale!",
                                       content="Adopt now!",
                                       publish_start_time=timezone.now() + timedelta(hours=-1),
                                       publish_end_time=timezone.now() + timedelta(hours=1),
                                       text_code="advert1",
                                       language=cls.language_en)

        cls.announcement3 = baker.make(Announcement, title="We got hacked",
                                       content="Hackers threaten to release incredibly sweet animal photos!",
                                       publish_start_time=timezone.now() + timedelta(hours=-1),
                                       publish_end_time=timezone.now() + timedelta(hours=1),
                                       text_code="hacked",
                                       language=cls.language_en)

        cls.announcement4 = baker.make(Announcement, title="New function: Nothing",
                                       content="You can now also do NOTHING on this side! NOTHING will help you to be "
                                               "more productive",
                                       publish_start_time=timezone.now() + timedelta(hours=1),
                                       publish_end_time=datetime.now() + timedelta(hours=2),
                                       text_code="inactive",
                                       language=cls.language_en)

        cls.announcement5 = baker.make(Announcement, title="Secret for all logged in",
                                       content="You can create adoption notices yourself",
                                       publish_start_time=timezone.now() + timedelta(hours=-1),
                                       publish_end_time=datetime.now() + timedelta(hours=2),
                                       text_code="secret",
                                       language=cls.language_en,
                                       logged_in_only=True)

    def test_active_announcements(self):
        active_announcements = Announcement.get_active_announcements()
        self.assertTrue(self.announcement1 in active_announcements)
        self.assertTrue(self.announcement2 in active_announcements)
        self.assertTrue(self.announcement3 in active_announcements)
        self.assertTrue(self.announcement4 not in active_announcements)
        self.assertTrue(self.announcement5 not in active_announcements)

        active_announcements = Announcement.get_active_announcements(language=self.language_de)
        self.assertTrue(self.announcement1 in active_announcements)
        self.assertTrue(self.announcement3 in active_announcements)
        self.assertTrue(self.announcement2 not in active_announcements)
        self.assertTrue(self.announcement4 not in active_announcements)
        self.assertTrue(self.announcement5 not in active_announcements)

        active_announcements = Announcement.get_active_announcements(language=self.language_de, logged_in=True)
        self.assertTrue(self.announcement1 in active_announcements)
        self.assertTrue(self.announcement3 in active_announcements)
        self.assertTrue(self.announcement2 not in active_announcements)
        self.assertTrue(self.announcement4 not in active_announcements)
        self.assertTrue(self.announcement5 in active_announcements)

