from django.test import TestCase


# Create your tests here.
class APITests(TestCase):
    def test_api(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response.json(), "Welcome to the API!")

    def test_health(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response.json(), "OK")


class APIGasTests(TestCase):
    def test_api_gas(self):
        response = self.client.get("/api/gas/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response.json(), "Welcome to the API!")
