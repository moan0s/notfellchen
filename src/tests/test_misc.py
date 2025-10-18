import datetime

from fellchensammlung.tools.misc import age_as_hr_string
from django.test import TestCase


class AgeTest(TestCase):

    def test_age_as_hr_string(self):
        self.assertEqual("7 Wochen", age_as_hr_string(datetime.timedelta(days=50)))
        self.assertEqual("3 Monate", age_as_hr_string(datetime.timedelta(days=100)))
        self.assertEqual("10 Monate", age_as_hr_string(datetime.timedelta(days=300)))
        self.assertEqual("1 Jahr und 4 Monate", age_as_hr_string(datetime.timedelta(days=500)))
        self.assertEqual("1 Jahr und 11 Monate", age_as_hr_string(datetime.timedelta(days=700)))
        self.assertEqual("2 Jahre und 6 Monate", age_as_hr_string(datetime.timedelta(days=900)))