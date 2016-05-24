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

### Translations ###

FinSL-signbank uses djangos translation feature and fetches translatable strings into django.po.

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

After you have written your translations, run:

    python bin/develop.py compilemessages yourlocale

This will compile the translations you wrote into django.po to django.mo file.
Remember to restart your server when doing this to make sure the new translations are in use.

### Contribution guidelines ###

If you want to contribute to the project, contact the repository administrator or University of Jyväskylä's Sign language centre.

### Who do I talk to? ###

@henrinie is admin of this repository.

* **Other community or team contact**

University of Jyväskylä, Sign language center (http://viittomakielenkeskus.jyu.fi/inenglish.html)

Finnish Association of the Deaf (http://www.kuurojenliitto.fi/en)
