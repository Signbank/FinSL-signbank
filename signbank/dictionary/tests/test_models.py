# -*- coding: utf-8 -*-
from django.test import TestCase
from signbank.dictionary.models import Gloss, Dataset, SignLanguage
from django.contrib.auth.models import User

from django.db import IntegrityError, DataError
from django.db import transaction


class GlossTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email=None, password=None)
        # Migrations have id=1 already
        self.signlanguage = SignLanguage.objects.create(pk=2, name="testsignlanguage", language_code_3char="tst")
        self.dataset = Dataset.objects.create(name="testdataset", signlanguage=self.signlanguage)
        Gloss.objects.create(idgloss="testgloss", dataset=self.dataset, created_by=self.user, updated_by=self.user)

    def test_string_representation(self):
        g = Gloss.objects.get(idgloss="testgloss")
        self.assertEqual(unicode(g), g.idgloss)

    def test_locked(self):
        """Test that locking Gloss works."""
        gloss = Gloss.objects.get(idgloss="testgloss")
        # Should be locked when first created
        self.assertFalse(gloss.locked)

        # Set locked True, and check that the Gloss is locked.
        gloss.locked = True
        gloss.save()
        self.assertTrue(gloss.locked)

    def test_unique_together(self):
        """Make sure that there can't be two of the same gloss+dataset combinations"""
        gloss = Gloss.objects.get(idgloss="testgloss")

        # Create another Gloss
        new_gloss = Gloss.objects.create(idgloss="testgloss2", dataset=self.dataset, created_by=self.user, updated_by=self.user)
        new_dataset = Dataset.objects.create(name="testdataset2", signlanguage=self.signlanguage)
        self.assertEqual(new_gloss.idgloss, "testgloss2")

        # Make sure you cannot violate unique_together by changing the Gloss.idgloss
        with self.assertRaises(IntegrityError):  # Should return IntegrityError
            with transaction.atomic():
                new_gloss.idgloss = "testgloss"
                new_gloss.save()

        # Change to a new dataset
        new_gloss.dataset = new_dataset
        new_gloss.save()
        self.assertTrue(new_gloss.dataset == new_dataset)

        # Change new_gloss to the same as gloss
        new_gloss.idgloss = "testgloss"
        new_gloss.save()
        self.assertTrue(new_gloss.idgloss == gloss.idgloss)

        # Make sure that you cannot violate unique_together by changing Dataset
        with self.assertRaises(IntegrityError):  # Should return IntegrityError
            with transaction.atomic():
                gloss.dataset = new_dataset
                gloss.save()

    def test_idgloss(self):
        """Tests idgloss"""
        gloss = Gloss.objects.get(idgloss="testgloss")

        # Check for some weird characters
        weird_chars = ("äöåÄÖÅ¨^~'* ´`üÜÿŸëêËÊ€$#", "ЁЂЃЄЅІЇЌЍЎЏАБВДЖИКОПРСТФХЦЧЩЫ", "؟ الستارود أي بعد, معاملة بيو",)
        for my_str in weird_chars:
            gloss.idgloss = my_str
            gloss.save()
            self.assertEqual(gloss.idgloss, str(gloss.idgloss))
            self.assertEqual(gloss.idgloss, my_str)

        # Test that the length of idgloss can't be too long
        with self.assertRaises(DataError):
            gloss.idgloss = "afasdkfjsdalkfjdsaljfl^¨'*´`} sajfljadsklfjasdklfjsadkjflÄÖÅlöjsadkfjasdkljflaksdjfkljdsfljasdlkfjakdslkafjsdlkafjölasdjfkldsajlaköfjsdakljfklasdjfkldsjaflkajdsflökjdsalkfjadslköfjdsalökjfklsdajflkdsjlkfajöldskjflkadsjflkdsajfladslkfjdlksa"
            gloss.save()

    def test_idgloss_dataset(self):
        """Test that a Gloss cannot be created without a relation to Dataset."""
        with self.assertRaises(IntegrityError):
            Gloss.objects.create(idgloss="testgloss7", created_by=self.user, updated_by=self.user)

    def test_idgloss_en(self):
        """Tests the field idgloss_en."""
        # Check that the max_length can't be exceeded.
        with self.assertRaises(DataError):
            en = Gloss.objects.create(idgloss="testgloss_en", idgloss_en="äöå1@r"*10+"1", dataset=self.dataset, created_by=self.user, updated_by=self.user)

    def test_created_by(self):
        """Tests that the created_by field functions when a gloss is created."""
        gl = Gloss.objects.create(idgloss="testgloss_createdby", dataset=self.dataset,
                             created_by=self.user, updated_by=self.user)
        self.assertEqual(gl.created_by, self.user)








