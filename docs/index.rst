.. FinSL-signbank documentation master file, created by
   sphinx-quickstart on Wed Jun 13 16:41:55 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============================
FinSL-signbank documentation
==============================
:Date: |today|
:Version: |version|

.. rubric:: FinSL-signbank is a Django web framework based application for
            managing *sign language* lexicons.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   settings
   translation
   changelog
   apps/index
   glossary

Features
--------

- Keep your sign language lexicon organized.
    - Have as many lexicons as you like.
    - Control user permissions per lexicon.
    - Publish your lexicons to be viewed by the public.
- Create Glosses and attach many kinds of data into them.
    - Videos: Record videos with a webcam in the app, or simply upload from your
      computer.
    - Translation equivalents in any language(s) you want.
    - Relationships between Glosses.
    - Sign language, notes, URLs, comments, etc.
- Separate user interfaces for viewing and editing detailed gloss data, and
  a non-editable interface for the public.
- Export you lexicon to be used with annotation of videos with `ELAN`_.
- The user interface is translated into several languages.
    - You can create translations for any language.
- View complete version history of Glosses and revert changes when needed.
- See a network graph of relationships between glosses per lexicon.

.. _ELAN: https://tla.mpi.nl/tools/tla-tools/elan/

.. _requirements_ref:

Requirements
------------

- Python 3.4
- Django 1.11
- PostgreSQL (or MySQL, SQLite3)
- Apache+mod_wsgi (or nginx)

Python dependencies are listed in `requirements.txt`_:

.. literalinclude:: ../requirements.txt
    :language: python

JavaScript dependencies are listed in `package.json`_:

.. literalinclude:: ../package.json
    :language: json


.. _requirements.txt: https://github.com/Signbank/FinSL-signbank/blob/master/requirements.txt
.. _package.json: https://github.com/Signbank/FinSL-signbank/blob/master/package.json


Installation (in short)
-----------------------

1. Install with pip: ``pip install finsl-signbank``.
2. Edit `settings files`_.
3. Migrate: ``python bin/develop.py migrate``

.. _settings files: https://github.com/Signbank/FinSL-signbank/tree/master/signbank/settings

.. note::
    See :ref:`installation` and :ref:`settings` for more detailed instructions.
