# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError, DataError
from django.db import transaction

from signbank.dictionary.models import (Gloss, Dataset, SignLanguage, Language, Keyword, Translation,
                                        Dialect, RelationToForeignSign, FieldChoice, MorphologyDefinition,
                                        GlossTranslations)
from signbank.dictionary.models import build_choice_list


class GlossTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email=None, password=None)
        # Migrations have id=1 already
        self.language = Language.objects.create(name="glang", language_code_2char="gl", language_code_3char="gla")
        self.signlanguage = SignLanguage.objects.create(pk=2, name="testsignlanguage", language_code_3char="tst")
        self.dataset = Dataset.objects.create(name="testdataset", signlanguage=self.signlanguage)
        self.gloss = Gloss.objects.create(idgloss="testgloss", dataset=self.dataset, created_by=self.user,
                                          updated_by=self.user)

    def test_str(self):
        self.assertEqual(str(self.gloss), self.gloss.idgloss)

    def test_publish(self):
        """Test that publishing Gloss works."""
        gloss = Gloss.objects.get(idgloss="testgloss")
        # Should be not be published when first created
        self.assertFalse(gloss.published)

        # Set locked True, and check that the Gloss is locked.
        gloss.published = True
        gloss.save()
        self.assertTrue(gloss.published)

    def test_unique_together(self):
        """Make sure that there can't be two of the same gloss+dataset combinations"""
        gloss = Gloss.objects.get(idgloss="testgloss")

        # Create another Gloss
        new_gloss = Gloss.objects.create(idgloss="testgloss2", dataset=self.dataset, created_by=self.user,
                                         updated_by=self.user)
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
            gloss.idgloss = "afasdkfjsdalkfjdsaljfl^¨'*´`} sajfljadsklfjasdklfjsadkjflÄÖÅlöjsadkfjasdkljflaksdjfkljds"
            "fljasdlkfjakdslkafjsdlkafjölasdjfkldsajlaköfjsdakljfklasdjfkldsjaflkajdsflökjdsalkfjadslköfjdsalökjfklsd"
            "ajflkdsjlkfajöldskjflkadsjflkdsajfladslkfjdlksa"
            gloss.save()

    def test_idgloss_dataset(self):
        """Test that a Gloss cannot be created without a relation to Dataset."""
        with self.assertRaises(IntegrityError):
            Gloss.objects.create(idgloss="testgloss7", created_by=self.user, updated_by=self.user)

    def test_idgloss_en(self):
        """Tests the field idgloss_en."""
        # Check that the max_length can't be exceeded.
        with self.assertRaises(DataError):
            en = Gloss.objects.create(idgloss="testgloss_en", idgloss_en="äöå1@r" * 10 + "1", dataset=self.dataset,
                                      created_by=self.user, updated_by=self.user)

    def test_created_by(self):
        """Tests that the created_by field functions when a gloss is created."""
        gl = Gloss.objects.create(idgloss="testgloss_createdby", dataset=self.dataset,
                                  created_by=self.user, updated_by=self.user)
        self.assertEqual(gl.created_by, self.user)

    def test_get_translation_languages(self):
        """Tests function get_translation_languages()"""
        self.dataset.translation_languages = (self.language,)
        self.dataset.save()
        self.assertIn(self.language, Gloss.get_translation_languages(self.gloss))

    def test_get_translations_for_translation_languages(self):
        """Test function get_translations_for_translation_languages()"""
        keyword = Keyword.objects.create(text="akeyword")
        keyword2 = Keyword.objects.create(text="another")
        translation = Translation.objects.create(gloss=self.gloss, language=self.language, keyword=keyword,
                                                      order=2)
        translation2 = Translation.objects.create(gloss=self.gloss, language=self.language, keyword=keyword2, order=3)
        self.dataset.translation_languages = (self.language,)
        self.dataset.save()
        unzipped = zip(*Gloss.get_translations_for_translation_languages(self.gloss))
        languages, translations = next(unzipped), next(unzipped)

        self.assertIn(self.language, languages)
        keywords = [str(translation.keyword), str(translation2.keyword)]
        # Check that all the keywords are in the 'translations' string.
        self.assertTrue(all(x in str(*translations) for x in keywords))

    def test_field_labels(self):
        """Test that function returns proper field labels."""
        meta_fields = self.gloss._meta.fields
        field_names = dict()
        for field in meta_fields:
            field_names[field.name] = field.verbose_name
        self.assertDictEqual(Gloss.field_labels(self.gloss), field_names)

    def test_get_fields(self):
        """Test function."""
        field_list = []
        for field in Gloss._meta.fields:
            field_list.append((field.name, field.value_to_string(self.gloss)))
        self.assertListEqual(Gloss.get_fields(self.gloss), field_list)


class DatasetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testdata", email=None, password=None)
        # Migrations have id=1 already
        self.signlanguage = SignLanguage.objects.create(pk=3, name="slang", language_code_3char="tst")
        self.dataset = Dataset.objects.create(name="dataset", signlanguage=self.signlanguage)

    def test_str(self):
        """Test unicode string representation."""
        self.assertEqual(str(self.dataset), self.dataset.name)


class GlossTranslationsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testglosstrans", email=None, password=None)
        (self.language1, created) = Language.objects.get_or_create(name="mylang", language_code_2char="er",
                                                                   language_code_3char="eor")
        (self.language2, created) = Language.objects.get_or_create(name="mylang2", language_code_2char="ir",
                                                                   language_code_3char="ior")
        (self.language3, created) = Language.objects.get_or_create(name="mylang3", language_code_2char="ar",
                                                                   language_code_3char="aor")
        (self.language4, created) = Language.objects.get_or_create(name="mylang4", language_code_2char="er",
                                                                   language_code_3char="eor")
        # Migrations have id=1 already for a SignLanguage
        (self.signlanguage, created) = SignLanguage.objects.get_or_create(pk=14, name="mysignlang",
                                                                          language_code_3char="mys")
        (self.dataset, created) = Dataset.objects.get_or_create(name="dataset52", signlanguage=self.signlanguage)
        (self.gloss, created) = Gloss.objects.get_or_create(idgloss="transgloss", dataset=self.dataset,
                                                            created_by=self.user, updated_by=self.user)
        (self.keyword, created) = Keyword.objects.get_or_create(text="tiger")
        # Create a Translation
        (self.translation, created) = Translation.objects.get_or_create(gloss=self.gloss, language=self.language1,
                                                                        keyword=self.keyword, order=1)
        # Create GlossTranslation objects
        self.translations = "squirrel, elephant, ant, magpie"
        self.translations_keywords = ["squirrel", "elephant", "ant", "magpie"]
        (self.glosstranslations, created) = \
            GlossTranslations.objects.get_or_create(gloss=self.gloss, language=self.language1,
                                                    translations=self.translations)
        self.translations_duplicates = "kangaroo, snake, kangaroo, horse, horse"
        self.translations_duplicates_keywords = ["kangaroo", "snake", "horse"]
        (self.glosstranslations_duplicates, created) = \
            GlossTranslations.objects.get_or_create(gloss=self.gloss, language=self.language2,
                                                    translations=self.translations_duplicates)

        self.translations_grouped = "1. cat, dog; 2. lion, crocodile; 3. mouse"
        self.translations_grouped_keywords = ["cat", "dog", "lion", "crocodile", "mouse"]

        (self.glosstranslations_grouped, created) = \
            GlossTranslations.objects.get_or_create(gloss=self.gloss, language=self.language3,
                                                    translations=self.translations_grouped)
        self.translations_grouped_duplicates = "1. kitten, pony; 2. monkey, pony; donkey, monkey"
        self.translations_grouped_duplicates_keywords = ["kitten", "pony", "monkey", "donkey"]
        (self.glosstranslations_grouped_duplicates, created) = \
            GlossTranslations.objects.get_or_create(gloss=self.gloss, language=self.language4,
                                                    translations=self.translations_grouped_duplicates)

    def test_get_keywords(self):
        """Test get_keywords()"""
        # Simple format
        self.assertEqual(self.glosstranslations.get_keywords(), self.translations_keywords)
        # Grouped format
        self.assertEqual(self.glosstranslations_grouped.get_keywords(), self.translations_grouped_keywords)

    def test_get_keywords_duplicates(self):
        """Make sure get_keywords() doesn't return duplicates."""
        # Simple format duplicates (keywords should not contain duplicates, translations field can)
        self.assertEqual(self.glosstranslations_duplicates.get_keywords_unique(), self.translations_duplicates_keywords)
        # Grouped format duplicates (keywords should not contain duplicates, translations field can)
        self.assertEqual(self.glosstranslations_grouped_duplicates.get_keywords_unique(),
                         self.translations_grouped_duplicates_keywords)

    def test_has_duplicates(self):
        """Tests has_duplicates() and verifies that it works correctly."""
        self.assertFalse(self.glosstranslations.has_duplicates())
        self.assertTrue(self.glosstranslations_duplicates.has_duplicates())
        self.assertFalse(self.glosstranslations_grouped.has_duplicates())
        self.assertTrue(self.glosstranslations_grouped_duplicates.has_duplicates())

    def test_save(self):
        """Test GlossTranslations.save()"""
        glosstrans = self.glosstranslations
        glosstrans.translations = "squirrel, magpie"  # Remove "elephant, ant"
        glosstrans.save()
        trans = Translation.objects.filter(gloss=self.gloss, language=self.language1)
        # Verify that these Translation objects have been deleted.
        self.assertFalse("elephant" and "ant" in [str(x.keyword) for x in trans])
        # Verify that these Translation objects still exist.
        self.assertTrue("squirrel" and "magpie" in [str(x.keyword) for x in trans])

    def test_save_duplicates(self):
        """Test saving duplicates."""
        # This object has duplicates, saving it should not raise exceptions.
        self.glosstranslations_duplicates.save()


class TranslationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testtrans", email=None, password=None)
        self.language = Language.objects.create(name="mylang", language_code_2char="ml", language_code_3char="myl")
        # Migrations have id=1 already for a SignLanguage
        self.signlanguage = SignLanguage.objects.create(pk=5, name="signlang", language_code_3char="sla")
        self.dataset = Dataset.objects.create(name="dataset", signlanguage=self.signlanguage)
        self.gloss = Gloss.objects.create(idgloss="transgloss", dataset=self.dataset, created_by=self.user,
                                          updated_by=self.user)
        self.keyword = Keyword.objects.create(text="myword")
        # Create a Translation
        self.translation = Translation.objects.create(gloss=self.gloss, language=self.language, keyword=self.keyword,
                                                      order=1)

    def test_str(self):
        """Test unicode string representation."""
        self.assertEqual(str(self.translation), self.keyword.text)


class KeywordTestCase(TestCase):
    def setUp(self):
        self.keyword = Keyword.objects.create(text="mykeyworD")

    def test_str(self):
        self.assertEqual(str(self.keyword), self.keyword.text)


class LanguageTestCase(TestCase):
    def setUp(self):
        self.language = Language.objects.create(name=u"New ÖÄ Language", language_code_2char="nl",
                                                language_code_3char="nla", description="New language we just created")

    def test_str(self):
        self.assertEqual(str(self.language), self.language.name)


class DialectTestCase(TestCase):
    def setUp(self):
        self.signlanguage = SignLanguage.objects.create(pk=5, name=u"sÄÄö", language_code_3char="ÄÄö")
        self.dialect = Dialect.objects.create(language=self.signlanguage, name=u"Northern sÄÄö",
                                              description=u"Northern sÄÄö has traditionally been used in the North "
                                                          u"Pole, But to this day it has also spread to Greenland.")

    def test_str(self):
        self.assertEqual(str(self.dialect), self.signlanguage.name + "/" + self.dialect.name)


class RelationToForeignSignTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testrel", email=None, password=None)
        self.signlanguage = SignLanguage.objects.create(pk=6, name="lala", language_code_3char="lal")
        self.dataset = Dataset.objects.create(name="relset", signlanguage=self.signlanguage)
        self.gloss = Gloss.objects.create(idgloss="related-GLOSS", dataset=self.dataset, created_by=self.user,
                                          updated_by=self.user)
        self.relation = RelationToForeignSign.objects.create(gloss=self.gloss, loan=True, other_lang=u"sÄÄö",
                                                             other_lang_gloss="Samp-GLOSS")

    def test_str(self):
        self.assertEqual(str(self.relation), self.gloss.idgloss + "/" + self.relation.other_lang + "," +
                         self.relation.other_lang_gloss)


class FieldChoiceTestCase(TestCase):
    def setUp(self):
        self.fieldchoice = FieldChoice.objects.create(field="field", english_name="mychoice", machine_value=1)

    def test_str(self):
        self.assertEqual(str(self.fieldchoice), self.fieldchoice.english_name)


class MorphologyDefinitionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="usermorph", email=None, password=None)
        self.signlanguage = SignLanguage.objects.create(pk=11, name="definitive", language_code_3char="def")
        self.dataset = Dataset.objects.create(name="morphdata", signlanguage=self.signlanguage)
        self.gloss = Gloss.objects.create(idgloss="morhp-gloss", dataset=self.dataset, created_by=self.user,
                                          updated_by=self.user)
        self.gloss2 = Gloss.objects.create(idgloss="morhp-gloss2", dataset=self.dataset, created_by=self.user,
                                           updated_by=self.user)
        self.fieldchoice = FieldChoice.objects.create(field="newfield", english_name="nice name", machine_value=2)
        self.morphdef = MorphologyDefinition.objects.create(parent_gloss=self.gloss, morpheme=self.gloss2,
                                                            role=self.fieldchoice)

    def test_str(self):
        self.assertEqual(str(self.morphdef), self.morphdef.morpheme.idgloss + " is " +
                         self.morphdef.role.english_name + " of " + self.morphdef.parent_gloss.idgloss)


class FunctionsTestCase(TestCase):
    def setUp(self):
        self.field = "testField"
        f1 = FieldChoice.objects.create(field=self.field, english_name="choice1", machine_value=1)
        f2 = FieldChoice.objects.create(field=self.field, english_name="choice_another", machine_value=2)
        f3 = FieldChoice.objects.create(field=self.field, english_name="full-of-choices", machine_value=3)
        self.choices = []
        self.choices.append((str(f1.machine_value), str(f1)))
        self.choices.append((str(f2.machine_value), str(f2)))
        self.choices.append((str(f3.machine_value), str(f3)))

    def test_build_choice_list(self):
        """Test that function returns proper values."""
        # TODO: Simulate OperationalError?
        self.assertListEqual(build_choice_list(self.field), self.choices)


