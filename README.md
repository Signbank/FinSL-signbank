# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

*   **Quick summary**
    * This is a repository for Signbank-fi (FinSL Signbank), a sign language Gloss database.
    * This version of Signbank is adjusted for the needs of Finnish sign language researchers.
    * FinSL Signbank is based on Dutch NGT Signbank (https://github.com/Signbank/NGT-signbank), which is a fork of Australian Auslan Signbank (https://github.com/Signbank/Auslan-signbank).
    * Easy to translate to various languages, it uses Django's translation engine paired with django-modeltranslation.
    * Can export Glosses directly to ELAN's controlled vocabulary
    * Signbank is built on django-framework version 1.8 and it is working on python 2.7.

*   **Version**

    * FinSL-signbank is currently in development.
    
### Wikipages ###

You can see our wiki at https://github.com/Signbank/FinSL-signbank/wiki

You can for example find information about installing Signbank-fi, its requirements and how to integrate it to ELAN.

### How do I get Signbank-fi set up? ###

*   **Summary of setup**

To install FinSL-signbank do:

    pip install -r /path/to/requirements.txt
    python bin/develop.py migrate
    python bin/develop.py runserver 127.0.0.1:8000

*   ** Configuration **

Before you can get FinSL-signbank working, you must change some paths in:

    signbank/settings/base.py  
    signbank/settings/development.py                              

* **Dependencies**

    See *requirements.txt*

*   **Database configuration**

Django should make all the needed database configurations apart from setting up a database.

    python bin/develop.py migrate

You can use sqlite3 for development

*   **How to run tests**

Tests are not yet available.

*   **Deployment instructions**

### Translations ###

FinSL-signbank uses djangos translation features and fetches strings to translate into django.po.

You can create new locales by:

    python bin/develop.py makemessages yourlocale

This creates django.po file for the locale you chose. Write translations inside msgstr:

    msgstr ""
    For example: msgstr "My translation of the text"

This is what the whole thing for one string/text looks like:

```
#!bash

    #. Translators: Button
    #: signbank/dictionary/templates/dictionary/gloss_detail.html:78
    msgid "Delete Sign"
    msgstr ""

```



After you have written your translations, do:

    python bin/develop.py compilemessages yourlocale

This will compile the translations you wrote into django.po to django.mo file.

### Contribution guidelines ###

This repository might not be actively maintained and that makes contribution a little harder.
If you want to contribute to the project, contact the repository administrator or University of Jyväskylä's Sign language centre.

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