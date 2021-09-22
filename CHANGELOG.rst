.. _changelog:

Changelog
=========

1.1.3 - 22/09/2021

**Migration required**

Allows setting the language for dataset glosses names
- Determines the language used to write the `idgloss` in
- This allows ELAN externally controlled vocabulary to have other than Finnish as the language

Makes it possible to add gloss relations across datasets
- New ajax endpoint for autocomplete
- Use idgloss field instead of gloss.id for target gloss in the form
- Show dataset/lexicon label in public and admin views

1.1.2 - 21/03/2020
------------------

**Add missing video app migrations that were squashed**

Before updating to this version, make sure you have done migrations for 1.0.1

1.1.1 - 21/03/2020
------------------

Update python and js dependencies, fix two js issues:

- Remove usage of deprecated error & success cb in $.ajax
- Return default empty array to js var in django template
- Update js dependencies: jQuery to 3.4.1 & bootstrap to 3.4.1
- Update js dependencies: cookieconsent to 3.1.1 & RecordRTC to 5.5.9
- Update django-bootstrap3 to 12.0.3
- Update django-contrib-comments to 1.9.2
- Update django-summernote to 0.8.11.6
- Update django-tagging to 0.5.0
- Update django-guardian to 2.2.0
- Update django-modeltranslation to 0.14.4

1.1.0 - 21/03/2020
------------------

**IMPORTANT: Make sure migrations in 1.0.1 are applied before moving to 1.1.0**

Before updating to this version, **make sure that you have applied the migrations in 1.0.1.**
Update to django 2.2 required changes to existing migration files. At the same time it was decided to squash the migrations.

- Django to 2.2.11

  * Migrations updated and squashed
  * Add ``on_delete`` to model fields
  * Updated url paths to use ``path()`` and ``path_re()``

- django-registration to 3.1

  * Introduces changes to template file locations and imports

- django-modeltranslation to 0.14
- Fix bug causing error in public gloss detail when video did not exist


1.0.1 - 14/03/2020
------------------

- Update dependencies

  * django-registration, django-reversion, django-notifications-hq, django-summernote

1.0.0 - dd/mm/2018
------------------

- First release
