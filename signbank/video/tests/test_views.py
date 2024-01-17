from django.contrib.auth.models import Permission, User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from guardian.shortcuts import assign_perm
from signbank.dictionary.models import (Dataset, FieldChoice, Gloss, Language,
                                        SignLanguage)
from signbank.video.models import GlossVideo
import csv


class UpdateGlossVideoTestCase(TestCase):
    def setUp(self):
        # Create user and add permissions
        self.user = User.objects.create_user(
            username="test", email=None, password="test")
        permission = Permission.objects.get(codename='change_glossvideo')
        self.user.user_permissions.add(permission)
        self.user.save()
        # Create client with change_gloss permission.
        self.client = Client()
        self.client.login(username="test", password="test")

        # Create user with change_gloss, but no view_dataset.
        self.user_nodataset = User.objects.create_user(
            username="nodataset", email=None, password="nodataset")
        self.user_nodataset.user_permissions.add(permission)
        self.user_nodataset.save()
        self.client_nodataset = Client()
        self.client_nodataset.login(username="nodataset", password="nodataset")

        # Create user with no permissions
        self.user_noperm = User.objects.create_user(
            username="noperm", email=None, password="noperm")
        self.user_noperm.save()
        self.client_noperm = Client()
        self.client_noperm.login(username="noperm", password="noperm")

        # Create client not logged in
        self.client_nologin = Client()

        # Create a gloss
        # Migrations have id=1 already
        self.signlanguage = SignLanguage.objects.create(
            pk=2, name="testsignlanguage", language_code_3char="tst")
        self.dataset = Dataset.objects.create(
            name="testdataset", signlanguage=self.signlanguage)
        self.testgloss = Gloss.objects.create(
            idgloss="testgloss", dataset=self.dataset, created_by=self.user, updated_by=self.user)
        self.language_en = Language.objects.create(
            name='English', language_code_2char='en', language_code_3char='eng')

        testfile = ContentFile(b'data \x00\x01')
        testfile.name = 'testvid.mp4'
        self.glossvid = GlossVideo.objects.create(gloss=self.testgloss, dataset=self.testgloss.dataset,
                                                  videofile=testfile)
        self.video_type = FieldChoice.objects.create(
            field="video_type", machine_value=1000, english_name="Test")

        # Assign view permissions to dataset for user
        assign_perm('view_dataset', self.user, self.dataset)

    def test_post_with_no_permission(self):
        """Test that you get 302 Found or 403 Forbidden if you try without permission."""
        response = self.client_noperm.post(reverse('video:glossvideo_update'), {
                                           'glossvideo': self.glossvid.pk, 'gloss': self.testgloss.pk, 'video_type': self.video_type.machine_value})
        # Make sure user does not have change_gloss permission.
        self.assertFalse(response.wsgi_request.user.has_perm(
            'video.manage_videos'))
        # Should return 302 Found, or 403 Forbidden
        self.assertIn(response.status_code, [403, 302])

    def test_post_nologin(self):
        """Testing POST with anonymous user."""
        response = self.client_nologin.post(reverse('video:glossvideo_update'), {
            'glossvideo': self.glossvid.pk, 'gloss': self.testgloss.pk, 'video_type': self.video_type.machine_value})
        # Should return 302 Found, or 403 Forbidden
        self.assertIn(response.status_code, [403, 302])

    def test_no_dataset_permission(self):
        """Test that the user can't update glosses if he doesn't have permissions to view the dataset of the gloss."""
        response = self.client_nodataset.post(reverse('video:glossvideo_update'), {
            'glossvideo': self.glossvid.pk, 'gloss': self.testgloss.pk, 'video_type': self.video_type.machine_value})
        self.assertEqual(response.status_code, 403)

    def test_update_glossvideo(self):
        """Test that the user can update the glossvideo"""
        response = self.client.post(reverse('video:glossvideo_update'), {
            'glossvideo': self.glossvid.pk, 'gloss': self.testgloss.pk, 'video_type': self.video_type.machine_value})
        self.assertEqual(response.status_code, 302)
        # Make sure that the response redirect url is correct.
        self.assertEqual(response.url, reverse('video:manage_videos'))

        """Test that the video type can be changed"""
        new_video_type = FieldChoice.objects.create(
            field="video_type", english_name="Test2", machine_value=1001)
        self.client.post(reverse('video:glossvideo_update'), {
            'glossvideo': self.glossvid.pk, 'gloss': self.testgloss.pk, 'video_type': new_video_type.machine_value})
        self.glossvid.refresh_from_db()
        self.assertEqual(self.glossvid.video_type, new_video_type)


class UpploadGlossVideoTestCase(TestCase):
    def setUp(self):
        # Create user and add permissions
        self.user = User.objects.create_user(
            username="test", email=None, password="test")
        permission = Permission.objects.get(codename='add_glossvideo')
        self.user.user_permissions.add(permission)
        self.user.save()
        # Create client with change_gloss permission.
        self.client = Client()
        self.client.login(username="test", password="test")

        # Create user with change_gloss, but no view_dataset.
        self.user_nodataset = User.objects.create_user(
            username="nodataset", email=None, password="nodataset")
        self.user_nodataset.user_permissions.add(permission)
        self.user_nodataset.save()
        self.client_nodataset = Client()
        self.client_nodataset.login(username="nodataset", password="nodataset")

        # Create user with no permissions
        self.user_noperm = User.objects.create_user(
            username="noperm", email=None, password="noperm")
        self.user_noperm.save()
        self.client_noperm = Client()
        self.client_noperm.login(username="noperm", password="noperm")

        # Create client not logged in
        self.client_nologin = Client()

        # Create a gloss
        # Migrations have id=1 already
        self.signlanguage = SignLanguage.objects.create(
            pk=2, name="testsignlanguage", language_code_3char="tst")
        self.dataset = Dataset.objects.create(
            name="testdataset", signlanguage=self.signlanguage)
        self.testgloss = Gloss.objects.create(
            idgloss="testgloss", dataset=self.dataset, created_by=self.user, updated_by=self.user)
        self.language_en = Language.objects.create(
            name='English', language_code_2char='en', language_code_3char='eng')

        self.testfile = SimpleUploadedFile(
            'testvid.mp4', b'data \x00\x01', content_type='video/mp4')
        self.video_type = FieldChoice.objects.create(
            field="video_type", machine_value=1000, english_name="Test")

        # Assign view permissions to dataset for user
        assign_perm('view_dataset', self.user, self.dataset)

    def test_post_with_no_permission(self):
        """Test that you get 302 Found or 403 Forbidden if you try without permission."""
        response = self.client_noperm.post(reverse('video:upload_glossvideo_gloss'), {
                                           'videofile': self.testfile, 'gloss': self.testgloss.pk, 'video_type': self.video_type.machine_value})
        # Make sure user does not have change_gloss permission.
        self.assertFalse(response.wsgi_request.user.has_perm(
            'video.add_glossvideo'))
        # Should return 302 Found, or 403 Forbidden
        self.assertIn(response.status_code, [403, 302])

    def test_post_nologin(self):
        """Testing POST with anonymous user."""
        response = self.client_nologin.post(reverse('video:upload_glossvideo_gloss'), {
            'videofile': self.testfile, 'gloss': self.testgloss.pk, 'video_type': self.video_type.machine_value})
        # Should return 302 Found, or 403 Forbidden
        self.assertIn(response.status_code, [403, 302])

    def test_no_dataset_permission(self):
        """Test that the user can't update glosses if he doesn't have permissions to view the dataset of the gloss."""
        response = self.client_nodataset.post(reverse('video:upload_glossvideo_gloss'), {
            'videofile': self.testfile, 'gloss': self.testgloss.pk, 'video_type': self.video_type.machine_value})
        self.assertEqual(response.status_code, 403)

    def test_upload_glossvideo(self):
        """Test that the user can upload the glossvideo"""
        response = self.client.post(reverse('video:upload_glossvideo_gloss'), {
            'videofile': self.testfile, 'gloss': self.testgloss.pk, 'video_type': self.video_type.machine_value})
        self.assertEqual(response.status_code, 302)
        # Make sure that the response redirect url is correct.
        self.assertEqual(response.url, "/")

        vid = self.testgloss.glossvideo_set.last()
        self.assertEqual(vid.title, "testvid.mp4")
        self.assertEqual(vid.video_type, self.video_type)

    def test_upload_glossvideo_with_custom_title(self):
        """Test that a custom title can be provided"""
        self.client.post(reverse('video:upload_glossvideo_gloss'), {
            'videofile': self.testfile, 'gloss': self.testgloss.pk, 'video_type': self.video_type.machine_value, 'title': 'Testtitle'})
        vid = self.testgloss.glossvideo_set.last()
        self.assertEqual(vid.title, 'Testtitle')

    def test_upload_glossvideo_with_custom_redirect(self):
        """Test that a custom redirect can be provided"""
        response = self.client.post(reverse('video:upload_glossvideo_gloss'), {
            'videofile': self.testfile, 'gloss': self.testgloss.pk, 'video_type': self.video_type.machine_value, 'redirect': reverse('video:manage_videos')})
        self.assertEqual(response.url, reverse('video:manage_videos'))

class ExportGlossvideoCsvTestCase(TestCase):
    def setUp(self):
        # Create user and add permissions
        self.user = User.objects.create_user(username="test")
        self.user.user_permissions.add(Permission.objects.get(codename='export_csv'))
        self.user.save()
        # Create client with export permission.
        self.client = Client()
        self.client.force_login(self.user)

        # Create user with no permissions
        self.user_noperm = User.objects.create_user(username="noperm")
        self.client_noperm = Client()
        self.client_noperm.force_login(self.user_noperm)

        # Create client not logged in
        self.client_nologin = Client()

        # Create a gloss
        # Migrations have id=1 already
        self.signlanguage = SignLanguage.objects.create(
            pk=2, name="testsignlanguage", language_code_3char="tst")
        self.dataset = Dataset.objects.create(
            name="testdataset", signlanguage=self.signlanguage)
        self.testgloss = Gloss.objects.create(
            idgloss="testgloss", dataset=self.dataset, created_by=self.user, updated_by=self.user)
        self.language_en = Language.objects.create(
            name='English', language_code_2char='en', language_code_3char='eng')

        testfile = SimpleUploadedFile(
            'testvid.mp4', b'data \x00\x01', content_type='video/mp4')
        self.glossvid = GlossVideo.objects.create(gloss=self.testgloss,
                                            is_public=False,
                                            dataset=self.testgloss.dataset,
                                            videofile=testfile)

    def test_export_csv_with_no_permission(self):
        response = self.client_noperm.get(reverse('video:export_glossvideos_csv'))
          # Make sure user does not have change_gloss permission.
        self.assertFalse(response.wsgi_request.user.has_perm(
            'dictionary.export_dictionary'))
        # Should return 302 Found, or 403 Forbidden
        self.assertIn(response.status_code, [403, 302])

    def test_export_csv(self):
        self.glossvid.is_public = True
        self.glossvid.save()

        response = self.client.get(reverse('video:export_glossvideos_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

        csv_data = b''.join(response.streaming_content).decode('utf-8')
        reader = csv.reader(csv_data.splitlines())
        csv_rows = list(reader)

        expected_glossvid_id = str(self.glossvid.pk)
        self.assertIn(expected_glossvid_id, [row[0] for row in csv_rows])


    def test_export_csv_with_not_public(self):
        response = self.client.get(reverse('video:export_glossvideos_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

        csv_data = b''.join(response.streaming_content).decode('utf-8')
        reader = csv.reader(csv_data.splitlines())
        csv_rows = list(reader)

        self.assertEqual(len(csv_rows), 1) # Header only
