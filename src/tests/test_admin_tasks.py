from datetime import timedelta
from django.utils import timezone

from fellchensammlung.tools.admin import get_unchecked_adoption_notices, deactivate_unchecked_adoption_notices, \
    deactivate_404_adoption_notices
from fellchensammlung.tools.misc import is_404
from django.test import TestCase

from model_bakery import baker
from fellchensammlung.models import AdoptionNotice


class DeactivationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        more_than_three_weeks_ago = now - timedelta(weeks=3, days=2)
        less_than_three_weeks_ago = now - timedelta(weeks=1, days=2)

        cls.adoption1 = baker.make(AdoptionNotice,
                                   name="TestAdoption1",
                                   created_at=more_than_three_weeks_ago)
        cls.adoption2 = baker.make(AdoptionNotice, name="TestAdoption2")
        cls.adoption3 = baker.make(AdoptionNotice,
                                   name="TestAdoption3",
                                   created_at=less_than_three_weeks_ago)

        cls.adoption1.set_active()
        cls.adoption1.last_checked = more_than_three_weeks_ago  # Reset updated_at to simulate test conditions
        cls.adoption1.save()
        cls.adoption3.set_active()
        cls.adoption3.last_checked = less_than_three_weeks_ago  # Reset updated_at to simulate test conditions
        cls.adoption3.save()

    def test_get_unchecked_adoption_notices(self):
        result = get_unchecked_adoption_notices()

        self.assertIn(self.adoption1, result)
        self.assertNotIn(self.adoption2, result)
        self.assertNotIn(self.adoption3, result)

    def test_deactivate_unchecked_adoption_notices(self):
        self.assertTrue(self.adoption1.is_active)
        self.assertFalse(self.adoption2.is_active)
        self.assertTrue(self.adoption3.is_active)

        deactivate_unchecked_adoption_notices()

        self.adoption1.refresh_from_db()
        self.adoption2.refresh_from_db()
        self.adoption3.refresh_from_db()

        self.assertFalse(self.adoption1.is_active)
        self.assertFalse(self.adoption2.is_active)
        self.assertTrue(self.adoption3.is_active)


class PingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        link_active = "https://hyteck.de/"
        link_inactive = "https://hyteck.de/maxwell"
        now = timezone.now()
        less_than_three_weeks_ago = now - timedelta(weeks=1, days=2)

        cls.adoption1 = baker.make(AdoptionNotice,
                                   name="TestAdoption1",
                                   created_at=less_than_three_weeks_ago,
                                   last_checked=less_than_three_weeks_ago,
                                   further_information=link_active)
        cls.adoption2 = baker.make(AdoptionNotice,
                                   name="TestAdoption2",
                                   created_at=less_than_three_weeks_ago,
                                   last_checked=less_than_three_weeks_ago,
                                   further_information=link_inactive)
        cls.adoption3 = baker.make(AdoptionNotice,
                                   name="TestAdoption3",
                                   created_at=less_than_three_weeks_ago,
                                   last_checked=less_than_three_weeks_ago,
                                   further_information=None)
        cls.adoption1.set_active()
        cls.adoption2.set_active()
        cls.adoption3.set_active()

    def test_is_404(self):
        urls = [("https://hyteck.de/maxwell", True),
                ("https://hyteck.de", False)]
        for url, expected_result in urls:
            self.assertEqual(is_404(url), expected_result)

    def test_deactivate_404_adoption_notices(self):
        self.assertTrue(self.adoption1.is_active)
        self.assertTrue(self.adoption2.is_active)
        deactivate_404_adoption_notices()
        self.adoption1.refresh_from_db()
        self.adoption2.refresh_from_db()
        self.assertTrue(self.adoption1.is_active)
        self.assertFalse(self.adoption2.is_active)

