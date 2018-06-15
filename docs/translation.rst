===========
Translation
===========

How to translate the user interface into a desired language, or how to edit
current translations?

Translating the interface is handled with Django's internalization features,
see `django translation docs
<https://docs.djangoproject.com/en/stable/topics/i18n/translation/>`_ for more
information.

Create a new language to translate to
-------------------------------------

Follow these instructions when you want to add a new language to translate to.

Add a new translation language
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before beginning translating the user interface into a new language, you need
to add the new language into the ``LANGUAGES`` setting in
**signbank/settings/base.py**.

.. code:: python

    # A list of all available languages. The list is a list of two-tuples in the
    # format (language code, language name) - for example, ('ja', 'Japanese').
    LANGUAGES = (
        ('fi', _('Finnish')),
        ('en', _('English')),
    )

You can find the correct ISO 639-1 codes here:
`<https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_

Make database migrations for django-modeltranslation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Django-modeltranslation is used to dynamically add translatable fields into
models. See django-modeltranslation docs here:
`<http://django-modeltranslation.readthedocs.io/en/latest/index.html>`_

After you have added a new language to the ``LANGUAGES`` setting, run the
following in the commandline in your **development** or **production**
environment

In development environment:

.. code:: bash

    $ python bin/development.py makemigrations
    $ python bin/development.py migrate

In production environment:

.. code:: bash

    $ python bin/production.py makemigrations
    $ python bin/production.py migrate

Create or update translations
-----------------------------

Create the translation file (.po)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You'll want to do this in your development environment.

.. code:: bash

    # -i venv ignores the python virtual environment folder.
    $ python bin/develop.py makemessages -i venv

For more information see:
`<https://docs.djangoproject.com/en/stable/ref/django-admin/#makemessages>`_

This command creates/updates the **django.po** files for all the ``LANGUAGES``.
These files will be created in **locale/<ISO 639-1 CODE>/LC_MESSAGES/django.po**

Write the translations
^^^^^^^^^^^^^^^^^^^^^^

To write the translations, open the **django.po** file. For each
``msgid "texthere"`` there is a ``msgstr ""`` where you should place the
translation of the text inside the quotes of msgstr.

For example the `locale/fi/LC_MESSAGES/django.po
<https://github.com/Signbank/FinSL-signbank/blob/master/locale/fi/LC_MESSAGES/django.po>`_
for Finnish translations:

.. include:: ../locale/fi/LC_MESSAGES/django.po
    :code: python
    :start-after: #:
    :end-before: #:

Once you have written the translations, make sure you put the new file on the
server (overwrite the old one).

To activate the translations in the application, you have to run the following
command which compiles the translation file :

In development:

.. code:: bash

    $ python bin/develop.py compilemessages

In production:

.. code:: bash

    $ python bin/production.py compilemessages
    # Make the server reload FinSL-signbank to update the translations.
    $ touch signbank/wsgi.py

For more information see:
`<https://docs.djangoproject.com/en/stable/ref/django-admin/#compilemessages>`_

Translate **Flat pages**
^^^^^^^^^^^^^^^^^^^^^^^^

Open the edit page for the Flat page you want to edit. For each Flat page you
should be able to translate the **title** and the **content** of the page. Each
language should have their own field for their version of the page, e.g.
**Title [fi]** and **Content [fi]**.
