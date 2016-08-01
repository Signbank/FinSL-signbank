# FinSL-signbank

**Store *Sign language* Gloss data with videos.**
FinSL-signbank aims to make the sign language annotation process more efficient.

Documentation is available at [https://github.com/Signbank/FinSL-signbank/wiki](https://github.com/Signbank/FinSL-signbank/wiki) 

# Overview

FinSL-signbank is being developed based on the needs of Finnish sign language researchers. It can be used for any sign language(s) that share similar requirements.
Signbank was originally developed by Steve Cassidy (https://github.com/Signbank/Auslan-signbank). FinSL-Signbank is being developed based on NGT Signbank (https://github.com/Signbank/NGT-signbank), NGT Signbank is a fork of Auslan Signbank.

Main features:
* Store Gloss data with multiple videos per Gloss.
* Interface easily translatable to multiple languages.
* Export Glosses as XML directly to ELAN (https://tla.mpi.nl/tools/tla-tools/elan/).
* Can store multiple datasets, even of the same language.
* Search from multiple datasets or just from one at a time.

# Requirements

* Python (2.7)
* Django (1.8)

# Documentation

You can find our wiki at https://github.com/Signbank/FinSL-signbank/wiki

The wiki has useful information about FinSL-Signbank:
* How to setup FinSL-signbank (pretty detailed guide).
* How to export Glosses from FinSL-signbank to ELAN.

# Installation

To install and test FinSL-signbank on linux:

    pip install -r /path/to/requirements.txt
    python bin/develop.py migrate
    python bin/develop.py runserver 127.0.0.1:8000

*   **Configuration**

Before you can get FinSL-signbank working, change some paths in:

    signbank/settings/base.py  
    signbank/settings/development.py                              

* **Dependencies**

    See https://github.com/Signbank/FinSL-signbank/blob/master/requirements.txt

*   **Database configuration**

Once you have created a database, and correctly configured the database in the settings, you are ready to migrate:

    python bin/develop.py migrate

*If you just want to test the application, we recommend using Sqlite3 as the database (as it is easy to set up)*

*   **How to run tests**

Tests are not yet available.

*   **Deployment instructions**

These can be found in our wiki:
https://github.com/Signbank/FinSL-signbank/wiki/Install

# Translations

FinSL-signbank uses djangos translation feature and fetches translatable strings into django.po.

You can create new locales by:

    python bin/develop.py makemessages yourlocale

This creates django.po file for the locale you chose. Write your translations inside msgstr:

    msgstr ""
    For example: msgstr "My translation of the text"

This is an example of one translated string/text:

```
#!bash

    #. Translators: Button
    #: signbank/dictionary/templates/dictionary/gloss_detail.html:78
    msgid "Delete Sign"
    msgstr "Your_translation_here"

```

After you have written your translations, run:

    python bin/develop.py compilemessages yourlocale

This will compile the translations you wrote into django.po to django.mo file.
Remember to restart your server when doing this to make sure the new translations are in use.

# Contribution

If you want to contribute to the project, contact the repository administrator @henrinie or University of Jyväskylä's Sign language centre (http://viittomakielenkeskus.jyu.fi/inenglish.html).
