from datetime import timedelta
from django.utils import timezone

from fellchensammlung.tools.admin import get_unchecked_adoption_notices, deactivate_unchecked_adoption_notices
from django.test import TestCase

from model_bakery import baker
from fellchensammlung.models import AdoptionNotice


class DeactiviationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        more_than_three_weeks_ago = now - timedelta(weeks=3, days=2)
        less_than_three_weeks_ago = now - timedelta(weeks=1, days=2)

        cls.adoption1 = baker.make(AdoptionNotice,
                                   name="TestAdoption1",
                                   created_at=more_than_three_weeks_ago,
                                   last_checked=more_than_three_weeks_ago)
        cls.adoption2 = baker.make(AdoptionNotice, name="TestAdoption2")
        cls.adoption3 = baker.make(AdoptionNotice,
                                   name="TestAdoption3",
                                   created_at=less_than_three_weeks_ago,
                                   last_checked=less_than_three_weeks_ago)

        cls.adoption1.set_active()
        cls.adoption3.set_active()

    def test_get_unchecked_adoption_notices(self):
        result = get_unchecked_adoption_notices()

        self.assertContains(result, self.adoption1)
        self.assertNotContains(result, self.adoption2)
        self.assertNotContains(result, self.adoption3)

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