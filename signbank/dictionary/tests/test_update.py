# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.core.files.base import ContentFile

from guardian.shortcuts import assign_perm

from signbank.dictionary.models import SignLanguage, Dataset, Gloss, Language
from signbank.video.models import GlossVideo


class UpdateGlossTestCase(TestCase):
    def setUp(self):
        # Create user and add permissions
        self.user = User.objects.create_user(username="test", email=None, password="test")
        permission = Permission.objects.get(codename='change_gloss')
        self.user.user_permissions.add(permission)
        self.user.save()
        # Create client with change_gloss permission.
        self.client = Client()
        self.client.login(username="test", password="test")

        # Create user with change_gloss, but no view_dataset.
        self.user_nodataset = User.objects.create_user(username="nodataset", email=None, password="nodataset")
        self.user_nodataset.user_permissions.add(permission)
        self.user_nodataset.save()
        self.client_nodataset = Client()
        self.client_nodataset.login(username="nodataset", password="nodataset")

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
        self.language_en = Language.objects.create(name="English", language_code_2char="en", language_code_3char="eng")
        self.dataset = Dataset.objects.create(name="testdataset", signlanguage=self.signlanguage, glosslanguage=self.language_en)
        self.testgloss = Gloss.objects.create(idgloss="testgloss", dataset=self.dataset, created_by=self.user, updated_by=self.user)
        

        # Assign view permissions to dataset for user
        assign_perm('view_dataset', self.user, self.dataset)

    def test_post_with_no_permission(self):
        """Test that you get 302 Found or 403 Forbidden if you try without permission."""
        response = self.client_noperm.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]), {'id': 'idgloss', 'value': 'TEST1_'})
        # Make sure user does not have change_gloss permission.
        self.assertFalse(response.wsgi_request.user.has_perm('dictionary.change_gloss'))
        # Should return 302 Found, or 403 Forbidden
        self.assertTrue(response.status_code == 403 or 302)

    def test_post_nologin(self):
        """Testing POST with anonymous user."""
        response = self.client_nologin.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]), {'id': 'idgloss', 'value': 'TEST_'})
        # Should return 302 Found, or 403 Forbidden
        self.assertTrue(response.status_code == 302 or 403)

    def test_no_dataset_permission(self):
        """Test that the user can't update glosses if he doesn't have permissions to view the dataset of the gloss."""
        response = self.client_nodataset.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]))
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        """Test HTTP GET"""
        response = self.client.get(reverse('dictionary:update_gloss', args=[self.testgloss.pk]))
        self.assertEqual(response.status_code, 405)

    def test_update_gloss(self):
        """Test that updating a gloss works."""
        new_idgloss = 'changed_idgloss'
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'idgloss', 'value': new_idgloss})
        self.assertEqual(response.status_code, 200)
        # After update, get the update object from db.
        self.testgloss.refresh_from_db()
        # Make sure the idgloss has been updated.
        self.assertTrue(self.testgloss.idgloss == new_idgloss)
        # Check that the updated_by user has been updated.
        self.assertTrue(self.testgloss.updated_by == response.wsgi_request.user)

        # Len value == 0 -> ' '
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'idgloss', 'value': ''})
        self.assertEqual(response.status_code, 200)
        # Make sure the returned value is bytes' '
        self.assertEqual(response.content.decode(), ' ')
        self.testgloss.refresh_from_db()
        self.assertEqual(self.testgloss.idgloss, ' ')

        # value[0] == '_'
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'idgloss', 'value': '_{s}'.format(s=new_idgloss)})
        self.assertEqual(response.status_code, 200)
        # Check that the underscore '_' is removed as first char.
        self.testgloss.refresh_from_db()
        self.assertEqual(self.testgloss.idgloss, new_idgloss)

        # Video_title

        test_title = 'Test video'
        new_title = 'new title'
        testfile = ContentFile(b'data \x00\x01')
        testfile.name = 'testvid.mp4'
        glossvid = GlossVideo.objects.create(title=test_title,
                                                  gloss=self.testgloss, dataset=self.testgloss.dataset,
                                                  videofile=testfile)
        self.assertEqual(glossvid.title, test_title)
        # Try to edit video title without change_glossvideo permission.
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'video_title{pk}'.format(pk=glossvid.pk), 'value': new_title})
        self.assertEqual(response.status_code, 403)

        # Add change_glossivideo permission to user.
        self.user.user_permissions.add(Permission.objects.get(codename='change_glossvideo'))
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'video_title{pk}'.format(pk=glossvid.pk), 'value': new_title})
        self.assertEqual(response.status_code, 200)
        glossvid.refresh_from_db()
        self.assertEqual(glossvid.title, new_title)
        if os.path.isfile(glossvid.videofile.path):
            # Remove the file.
            os.remove(glossvid.videofile.path)

        # Test updating title for nonexisting glossvideo.
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'video_title{pk}'.format(pk=glossvid.pk+93214596), 'value': new_title})
        self.assertEqual(response.status_code, 400)

        # Test translating booleanfield to string 'Yes'
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'alternating_movement', 'value': True})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.decode())

        # Test updating empty value, should set field to None.
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'phonology_other', 'value': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), ' ')
        self.testgloss.refresh_from_db()
        self.assertEqual(self.testgloss.phonology_other, ' ')

    def test_update_nonexisting_field(self):
        """Test updating non-existing gloss field."""
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'nonexistingfield', 'value': 'whatever'})
        # Check for Bad Request 400
        self.assertEqual(response.status_code, 400)

    def test_update_glossurl(self):
        """Test updating glossurl."""
        create_value = 'http://localhost'
        # Create a glossurl
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'glossurl-create', 'value': create_value})
        # HttpResponseRedirect returns 302
        self.assertEqual(response.status_code, 302)
        # Make sure that the response redirect url is correct.
        self.assertEqual(response.url, reverse('dictionary:admin_gloss_view', args=[self.testgloss.pk]))
        glossurl = self.testgloss.glossurl_set.get(url=create_value)
        # Check that the created glossurl exists in db.
        self.assertTrue(glossurl)

        update_value = 'http://localhost/test'
        # Update the created glossurl value
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'glossurl-{pk}'.format(pk=glossurl.pk),
                                     'value': update_value})
        # Make sure it returns status OK 200.
        self.assertEqual(response.status_code, 200)
        # Check that the value was updated into the db.
        self.assertTrue(self.testgloss.glossurl_set.get(url=update_value))

        # Try to update non-existing glossurl.
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'glossurl-1587665423',
                                     'value': update_value})
        # Updating non-existing glossurl should not have effect.
        self.assertEqual(response.status_code, 200)

    def test_update_keyword(self):
        """Test updating keywords/translations."""
        keywords = '1. dog, cat; 2. pet'
        keywords_parsed = ['dog', 'cat', 'pet']
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'keywords_{lang}'.format(lang=self.language_en.language_code_2char),
                                     'value': keywords})
        self.assertEqual(response.status_code, 200)
        # Check that all the created keywords exist.
        [self.assertTrue(self.testgloss.translation_set.get(keyword__text=x,
                                                            language=self.language_en)) for x in keywords_parsed]

        # Try to update keywords for nonexisting language, expect 400.
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'keywords_åå', 'value': keywords})
        self.assertEqual(response.status_code, 400)

        # Update keywords for duplicate language_code_2char, expect 400.
        duplicate_lang = Language.objects.create(name='TestLang', language_code_2char='en', language_code_3char='eng')
        response = self.client.post(reverse('dictionary:update_gloss', args=[self.testgloss.pk]),
                                    {'id': 'keywords_{lang}'.format(lang=self.language_en.language_code_2char),
                                     'value': keywords})
        self.assertEqual(response.status_code, 400)