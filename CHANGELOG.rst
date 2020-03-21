.. _changelog:

Changelog
=========

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
