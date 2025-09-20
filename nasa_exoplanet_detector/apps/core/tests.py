from django.test import TestCase
from django.urls import reverse

class SmokeTests(TestCase):
    def test_dashboard(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)
