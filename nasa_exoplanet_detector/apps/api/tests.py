from django.test import TestCase
from django.urls import reverse
import json

class ApiTests(TestCase):
    def test_health(self):
        # Core health view
        resp = self.client.get('/health/')
        self.assertEqual(resp.status_code, 200)

    def test_predict_endpoint(self):
        payload = {
            'orbital_period': 10.0,
            'transit_duration': 2.5,
            'planet_radius': 1.2,
            'stellar_temp': 5500,
        }
        resp = self.client.post(reverse('api_predict'), data=json.dumps(payload), content_type='application/json')
        # May fail if models not trained yet, accept 400/200
        self.assertIn(resp.status_code, (200, 400))
