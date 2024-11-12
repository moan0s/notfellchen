from django.test import TestCase
from fellchensammlung.forms import AdoptionNoticeFormWithDateWidgetAutoAnimal
from fellchensammlung.models import Species
from model_bakery import baker


class TestAdoptionNoticeFormWithDateWidgetAutoAnimal(TestCase):
    @classmethod
    def setUpTestData(cls):
        rat = baker.make(Species, name="Farbratte")

    def test_forms(self):
        form_data = {"name": "TestAdoption3",
                     "species": Species.objects.first(),
                     "num_animals": "2",
                     "date_of_birth": "2024-11-04",
                     "sex": "M",
                     "group_only": "on",
                     "searching_since": "2024-11-10",
                     "location_string": "Mannheim",
                     "description": "Blaaaa",
                     "further_information": "https://notfellchen.org",
                     "save-and-add-another-animal": "Speichern"}
        form = AdoptionNoticeFormWithDateWidgetAutoAnimal(data=form_data)
        self.assertTrue(form.is_valid())
