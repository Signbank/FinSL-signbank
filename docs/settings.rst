.. _settings:

========
Settings
========

Here you can find explanations for some of the settings, and how the settings
files are distributed.

The different settings files
----------------------------

You can find all the settings files in the directory ``signbank/settings/``.

There are several different files for different purposes:

- **base.py**: settings shared with all environments.
- **production.py**: production environment specific settings.
- **development.py**: development environment specific settings.
- **testing.py**: settings for tests.
- **settings_secret.py**:
    - Settings you don't want push to a public git repository.
    - ``SECRET_KEY`` and database passwords and such.

base.py
^^^^^^^^^^^^^^

.. currentmodule:: signbank.settings.base

.. autodata:: ACCOUNT_ACTIVATION_DAYS
    :annotation:
.. autodata:: AUTHENTICATION_BACKENDS
    :annotation:
.. autodata:: INSTALLED_APPS
    :annotation:
.. autodata:: LANGUAGES
    :annotation:
.. autodata:: LANGUAGE_CODE
    :annotation:
.. autodata:: LOGIN_REDIRECT_URL
    :annotation:
.. autodata:: MIDDLEWARE
    :annotation:

.. autodata:: REGISTRATION_OPEN
    :annotation:

.. autodata:: STATICFILES_FINDERS
    :annotation:
.. autodata:: TIME_ZONE
    :annotation:
.. autodata:: USE_I18N
    :annotation:
.. autodata:: USE_L10N
    :annotation:
.. autodata:: USE_TZ
    :annotation:
.. autodata:: VIDEO_UPLOAD_LOCATION
    :annotation:

development.py
^^^^^^^^^^^^^^

.. currentmodule:: signbank.settings.development

.. autodata:: DEBUG
    :annotation:
.. autodata:: EMAIL_BACKEND
    :annotation:
.. autodata:: LOCALE_PATHS
    :annotation:

production.py
^^^^^^^^^^^^^^

.. currentmodule:: signbank.settings.production

.. autodata:: ALLOWED_HOSTS
    :annotation:
.. autodata:: CACHES
    :annotation:
.. autodata:: DEBUG
    :annotation:
.. autodata:: DO_LOGGING
    :annotation:
.. autodata:: EMAIL_BACKEND
    :annotation:
.. autodata:: LOGGING
    :annotation:
.. autodata:: MEDIA_ROOT
    :annotation:
.. autodata:: STATIC_ROOT
    :annotation:
.. autodata:: UPLOAD_ROOT
    :annotation:

settings_secret.py
^^^^^^^^^^^^^^^^^^

.. currentmodule:: signbank.settings.settings_secret

.. py:data:: ADMINS

    A list of all the people who get code error notifications. When DEBUG=False and a view raises an exception, Django will email these people with the full exception information.

.. py:data:: DATABASES

    A dictionary containing the settings for all databases to be used with Django.

.. py:data:: DB_IS_PSQL

    Is the database engine used is postgresql?

.. py:data::  PSQL_DB_QUOTA

    Maximum size of database in bytes, controlled outside of this application. Fill it in if you have a quota.

.. py:data:: PSQL_DB_NAME

    The name of a database used.

.. py:data:: DEFAULT_FROM_EMAIL

    Default email address to use for various automated correspondence from the site manager(s). Note: You can also use the following form ‘Webmaster <webmaster@yourdomain.com>’

.. py:data:: EMAIL_HOST

    The host to use for sending email.

.. py:data:: EMAIL_PORT

    Port to use for the SMTP server defined in EMAIL_HOST.

.. py:data:: SECRET_KEY

    Make this unique, and don’t share it with anybody. This is used to provide cryptographic signing.

.. py:data:: SERVER_EMAIL

    The email address that error messages come from, such as those sent to ADMINS and MANAGERS. Note: You can also use the following form ‘Webmaster <webmaster@yourdomain.com>’

testing.py
^^^^^^^^^^

The **testing.py** settings file currently only imports **development.py**
settings.
Edit this file to customize test settings when runnings tests with
**bin/runtests.py**.

When is which settings file applied?
------------------------------------

By default when creating a new django project, a **manage.py** file is created.
It is used to run all the management commands, and it applies all the settings.

FinSL-signbank useses separate management files to make it easier to run
management commands in different environments with different settings. You
can find these files in the **bin/** folder:

.. note::
    **base.py** holds shared settings, and is imported in every settings file.
    **settings_secret.py** is then imported in **base.py**.

* **develop.py**: to run the development environment with ``development.py`` settings.

* **production.py**: to run management commands with ``production.py`` settings.

* **runtests.py**: to run management commands with ``testing.py`` settings.
