from django.test import TestCase
from django.urls import reverse

from docs.conf import language
from fellchensammlung.models import User, TrustLevel, AdoptionNotice, Species, Rule, Language
from model_bakery import baker


class BasicViewTest(TestCase):
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

        ans = []
        for i in range(0, 8):
            ans.append(baker.make(AdoptionNotice, name=f"TestAdoption{i}"))
        for i in range(0, 4):
            AdoptionNotice.objects.get(name=f"TestAdoption{i}").set_active()

        Rule.objects.create(title="Rule 1", rule_text="Description of r1", rule_identifier="rule1", language=Language.objects.get(name="English"))

    def test_index_logged_in(self):
        self.client.login(username='testuser0', password='12345')

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser0')
        self.assertContains(response, "TestAdoption0")
        self.assertNotContains(response, "TestAdoption5")  # Should not be active, therefore not shown

    def test_index_anonymous(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestAdoption1")
        self.assertNotContains(response, "TestAdoption4")  # Should not be active, therefore not shown

    def test_about_logged_in(self):
        self.client.login(username='testuser0', password='12345')
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rule 1")

    def test_about_anonymous(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rule 1")

    def test_report_adoption_logged_in(self):
        self.client.login(username='testuser0', password='12345')
        an = AdoptionNotice.objects.get(name="TestAdoption0")
        response = self.client.get(reverse('report-adoption-notice', args=str(an.pk)))
        self.assertEqual(response.status_code, 200)

        data = {"reported_broken_rules": 1, "user_comment": "animal cruelty"}
        response = self.client.post(reverse('report-adoption-notice', args=str(an.pk)), data=data)
        self.assertEqual(response.status_code, 302)

    def test_report_adoption_anonymous(self):
        an = AdoptionNotice.objects.get(name="TestAdoption0")
        response = self.client.get(reverse('report-adoption-notice', args=str(an.pk)))
        self.assertEqual(response.status_code, 200)

        data = {"reported_broken_rules": 1, "user_comment": "animal cruelty"}
        response = self.client.post(reverse('report-adoption-notice', args=str(an.pk)), data=data)
        self.assertEqual(response.status_code, 302)
