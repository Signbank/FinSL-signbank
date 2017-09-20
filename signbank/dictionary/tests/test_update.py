# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission

from guardian.shortcuts import assign_perm

from signbank.dictionary.models import SignLanguage, Dataset, Gloss


class UpdateGlossTestCase(TestCase):
    def setUp(self):
        # Create user and add permissions
        self.user = User.objects.create_user(username="test", email=None, password="test")
        permission = Permission.objects.get(codename='change_gloss')
        self.user.user_permissions.add(permission)
        self.user.save()
        # Create client for user with permission
        self.client = Client()
        self.client.login(username="test", password="test")

        # Create user with no permissions
        self.user_noperm = User.objects.create_user(username="noperm", email=None, password="noperm")
        self.user_noperm.save()
        self.client_noperm = Client()
        self.client_noperm.login(username="noperm", password="noperm")

        # Create client not logged in
        self.client_nologin = Client()

        # Create a gloss
        # Migrations have id=1 already
        self.signlanguage = SignLanguage.objects.create(pk=2, name="testsignlanguage", language_code_3char="tst")
        self.dataset = Dataset.objects.create(name="testdataset", signlanguage=self.signlanguage)
        self.testgloss = Gloss.objects.create(idgloss="testgloss", dataset=self.dataset, created_by=self.user, updated_by=self.user)

    def test_post_with_no_permission(self):
        """Test that you get 302 Found or 403 Forbidden if you try without permission."""
        response = self.client_noperm.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]), {'id': 'idgloss', 'value': 'TEST_'})
        # Should return 302 Found, or 403 Forbidden
        self.assertTrue(response.status_code == 302 or 403)

    def test_post_nologin(self):
        """Testing POST with anonymous user."""
        response = self.client_nologin.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]), {'id': 'idgloss', 'value': 'TEST_'})
        # Should return 302 Found, or 403 Forbidden
        self.assertTrue(response.status_code == 302 or 403)

    def test_no_dataset_permission(self):
        """Test that the user can't update glosses if he doesn't have permissions to view the dataset of the gloss."""
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]))
        self.assertEqual(response.status_code, 403)

    def test_delete_gloss_no_permission(self):
        """Test deleting a gloss with no permission, should not be possible."""
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'deletegloss', 'value': 'confirmed'})
        # Should return 403 Forbidden, since the user does not have permission dictionary.delete_gloss
        self.assertEqual(response.status_code, 403)

    def test_delete_gloss(self):
        """Test deleting a gloss with permission dictionary.delete_gloss."""
        # Add permission to delete gloss.
        permission_del = Permission.objects.get(codename='delete_gloss')
        permission_change = Permission.objects.get(codename='change_gloss')
        self.user.user_permissions.add(permission_del, permission_change)
        self.user.save()
        # Give the user permission to view objects of the glosses dataset.
        assign_perm('view_dataset', self.user, self.testgloss.dataset)
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'deletegloss', 'value': 'confirmed'})
        # HttpResponseRedirect = 302 Found
        self.assertEqual(response.status_code, 302)




