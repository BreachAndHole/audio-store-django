from django.test import TestCase


class URLTests(TestCase):
    def test_index_page_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_all_cables_page_url(self):
        response = self.client.get('/cables/')
        self.assertEqual(response.status_code, 200)

    def test_login_page_url(self):
        response = self.client.get('/user/login/')
        self.assertEqual(response.status_code, 200)

    def test_register_page_url(self):
        response = self.client.get('/user/registration/')
        self.assertEqual(response.status_code, 200)
