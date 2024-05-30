from django.test import TestCase
from django.contrib.auth.models import Permission
from django.urls import reverse

from model_bakery import baker

from fellchensammlung.models import Animal, Species, AdoptionNotice, User

class AnimalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user0 = User.objects.create_user(username='testuser0',
                                              first_name="Admin",
                                              last_name="BOFH",
                                              password='12345')
        permission_view_user = Permission.objects.get(codename='view_member')
        test_user0.user_permissions.add(permission_view_user)

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

    def test_detail(self):
        self.client.login(username='testuser0', password='12345')

        response = self.client.post(reverse('animal-detail', args="1"))
        self.assertEqual(response.status_code, 200)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser0')
        self.assertContains(response, "Rat1")
