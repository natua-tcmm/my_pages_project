from django.test import TestCase


class RedirectSiteRoutingTests(TestCase):
    def test_top_page_contains_new_site_url(self):
        response = self.client.get("/my_apps/top")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://www.st1027.org")

    def test_chunithm_rating_page_contains_target_url(self):
        response = self.client.get("/my_apps/chunithm_rating_all")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://www.st1027.org/tools/chunithm_rating_all")

    def test_const_search_page_contains_target_url(self):
        response = self.client.get("/my_apps/const_search")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://www.st1027.org/tools/const_search")

    def test_ongeki_rating_page_contains_target_url(self):
        response = self.client.get("/my_apps/ongeki_rating_all")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://www.st1027.org/tools/ongeki_rating_all")

    def test_ongeki_op_page_contains_target_url(self):
        response = self.client.get("/my_apps/ongeki_op")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://www.st1027.org/tools/ongeki_op")

    def test_legacy_page_redirects_to_top(self):
        response = self.client.get("/my_apps/fullbell")
        self.assertRedirects(response, "/my_apps/top")

    def test_root_redirects_to_my_apps_top(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/my_apps/top")
