# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

*   ** Quick summary **
    * This is a repository for Signbank-fi, a sign language Gloss database.
    * This version of Signbank is adjusted for the needs of Finnish sign language researchers.
    * Signbank-fi is based on Dutch Signbank (https://github.com/Woseseltops/signbank), which is a fork of Australian Signbank (https://bitbucket.org/stevecassidy/signbank).
    * Signbank-fi is easy to translate to various languages, it uses Django's translation engine paired with django-modeltranslation. 
    * Signbank is built on django-framework version 1.8 and it is working on python 2.7.

*   ** Version **

    * Signbank-fi is currently in development.

### How do I get Signbank-fi set up? ###

*   ** Summary of set up **

To install Signbank-fi do:

    pip install -r /path/to/requirements.txt
    python bin/develop.py migrate
    python bin/develop.py runserver 127.0.0.1:8000

*   ** Configuration **

Before you can get Signbank-fi working, you must change some paths in:  

    signbank/settings/base.py  
    signbank/settings/development.py                              

* ** Dependencies **

    See *requirements.txt*

*   ** Database configuratio n**

Django should make all the needed database configurations apart from setting up a database.

    bin/develop.py migrate

You can use sqlite3 for development

*   ** How to run tests **

Tests are not yet available.

*   ** Deployment instructions **

### Translations ###

Signbank-fi uses djangos translation features and fetches strings to translate into django.po.

You can create new locales by:

    python bin/develop.py makemessages yourlocale

This creates django.po file for the local you want. Write translations inside msgstr:

    msgstr ""
    For example: msgstr "My translation of the text"

This is what the whole thing for one string/text looks like:

    \#. Translators: Button
    \#: signbank/dictionary/templates/dictionary/gloss_detail.html:78
    msgid "Delete Sign"
    msgstr ""


After you have written your translations, do:

    python bin/develop.py compilemessages yourlocale

This will compile the translations you wrote into django.po to django.mo

### Contribution guidelines ###

This repository might not be actively maintained and that makes contribution a little harder.

* Writing tests

If you are willing to contribute to this repository, writing tests would be a good way to help.

Before doing anything, contact the admin of this repository for discussion.

* Code review
* Other guidelines

### Who do I talk to? ###

* **Repo owner or admin**

Henri Nieminen, admin of this repository

* **Other community or team contact**

University of Jyväskylä, Sign language center (http://viittomakielenkeskus.jyu.fi/inenglish.html)

Finnish Association of the Deaf (http://www.kuurojenliitto.fi/en)