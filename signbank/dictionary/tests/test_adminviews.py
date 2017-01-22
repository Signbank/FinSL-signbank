# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser, User, Permission


class GlossListViewTestCase(TestCase):
    def setUp(self):
        # Create user and add permissions
        self.user = User.objects.create_user(username="test", email=None, password="test")
        permission = Permission.objects.get(codename='search_gloss')
        self.user.user_permissions.add(permission)
        self.user.save()
        # Create client for user with permission
        self.client = Client()
        self.client.login(username="test", password="test")

        # Create user with no permission
        self.user_noperm = User.objects.create_user(username="noperm", email=None, password="noperm")
        self.user_noperm.save()
        # Create client for user with no permission
        self.client_noperm = Client()
        self.client_noperm.login(username="noperm", password="noperm")

    def test_get_user_not_authenticated(self):
        """Test that non-authenticated user can't access the search page via GET."""
        self.client.logout()
        response = self.client.get(reverse('admin_gloss_list'))
        self.assertFalse(response.status_code == 200)

    def test_get_user_authenticated_has_permission(self):
        """Tests that an authenticated user with proper permissions can access search page via GET."""
        response = self.client.get(reverse('admin_gloss_list'))
        self.assertTrue(response.status_code == 200)

    def test_get_user_authenticated_no_permission(self):
        """Tests that authenticated user without proper permission can't access search page via GET."""
        # Using client_noperm
        response = self.client_noperm.get(reverse('admin_gloss_list'))
        self.assertFalse(response.status_code == 200)
        # 302 Found
        self.assertTrue(response.status_code == 302)

    def test_post(self):
        """Testing that the search page can't be accessed with POST."""
        response = self.client.post(reverse('admin_gloss_list'))
        # 405 Method Not Allowed
        self.assertTrue(response.status_code == 405)

    def test_put(self):
        """Tests that PUT doesn't work on search page."""
        response = self.client.put(reverse('admin_gloss_list'))
        # 405 Method Not Allowed
        self.assertTrue(response.status_code == 405)

    def test_delete(self):
        """Tests that DELETE doesn't work on search page."""
        response = self.client.delete(reverse('admin_gloss_list'))
        # 405 Method Not Allowed
        self.assertTrue(response.status_code == 405)