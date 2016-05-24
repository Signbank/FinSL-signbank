# README #

### What is this repository for? ###

This is a repository for FinSL-signbank, a web application for storing *Sign language* Glosses with videos.
The purpose of FinSL-signbank is to make the sign language annotation process more efficient, and to be able to store Glosses.

*   **Quick summary**
    * FinSL-signbank is being developed based on the needs of Finnish sign language researchers
    * This application can be used for any Sign language(s) if the requirements are similar.
    * Signbank was originally developed by Steve Cassidy (https://github.com/Signbank/Auslan-signbank)
    * FinSL-Signbank is being developed based on NGT Signbank (https://github.com/Signbank/NGT-signbank), NGT Signbank is a fork of Auslan Signbank.
   
*   **Main features**
    * Store Glosses with videos and relevant data.
    * Interface easily translatable to multiple languages.
    * Export Glosses as XML directly to ELAN (https://tla.mpi.nl/tools/tla-tools/elan/).
    * Holds multiple datasets, even of the same language.
    * Search from within multiple datasets or just from one at a time.

*   **About the application**
    * Built with django-framework 1.8 and python 2.7.
    * Currently in development and no official releases exist yet..
    
### Wiki ###

You can find our wiki at https://github.com/Signbank/FinSL-signbank/wiki

The wiki has useful information considering FinSL-Signbank:
    * How to setup FinSL-signbank (pretty detailed guide).
    * How to export Glosses from FinSL-signbank to ELAN.

### Summary of setup ###

To install and test FinSL-signbank on linux:

    pip install -r /path/to/requirements.txt
    python bin/develop.py migrate
    python bin/develop.py runserver 127.0.0.1:8000

*   ** Configuration **

Before you can get FinSL-signbank working, you must change some paths in:

    signbank/settings/base.py  
    signbank/settings/development.py                              

* **Dependencies**

    See https://github.com/Signbank/FinSL-signbank/blob/master/requirements.txt

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
