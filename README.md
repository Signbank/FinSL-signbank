# FinSL-signbank

[![Dependency Status](https://www.versioneye.com/user/projects/583fd43dc68b120012d0f5e1/badge.svg?style=flat-square)](https://www.versioneye.com/user/projects/583fd43dc68b120012d0f5e1)
![coverage](https://rawgit.com/Signbank/FinSL-signbank/master/coverage.svg)



**Store *Sign language* Gloss data with videos.**

FinSL-signbank is a web application that aims to make the *sign language* annotation process more efficient.

Documentation is available at [https://github.com/Signbank/FinSL-signbank/wiki][wiki]

# Overview

FinSL-signbank is being developed based on the needs of Finnish sign language researchers. It can be used for any sign language(s) that share similar requirements.
Signbank was originally developed by Steve Cassidy [https://github.com/Signbank/Auslan-signbank][auslan-signbank]. FinSL-Signbank is being developed based on NGT Signbank [https://github.com/Signbank/NGT-signbank][ngt-signbank], NGT Signbank is a fork of Auslan Signbank.

Main features:
* Store Glosses with data and multiple videos per Gloss.
* Record videos with webcam on the website.
* Upload multiple videos at once, then connect them with Glosses later.
* Interface easily translatable to multiple languages.
* Export Glosses directly to [ELAN][elan-link].
* Store multiple datasets, even of the same language.
*

# Requirements

* Python (2.7)
* Django (1.10)

Dependencies can be found in [requirements.txt][requirements.txt] and they can be installed using pip.

# Documentation

You can find documentation in our [wiki][wiki].

# Installation

To install FinSL-signbank on linux with all the dependencies:

    pip install -r /path/to/finsl-signbank/requirements.txt

**Configuration**

Before you can get FinSL-signbank working, change some paths in:

    signbank/settings/base.py
    signbank/settings/development.py

Rename settings_secret.py.template to settings_secret.py and fill in the necessary information:

    mv settings_secret.py.template settings_secret.py

**Database configuration**

Once you have created a database, and correctly configured the database in the settings, you are ready to migrate:

    python bin/develop.py migrate

*If you just want to test the application, we recommend using [Sqlite3][sqlitelink] as the database (as it is fast and easy to set up)*

**Running the application**

When you are ready to test your FinSL-Signbank installation, run:

    python bin/develop.py runserver 127.0.0.1:8000

Then open your web browser on http://127.0.0.1:8000

When you are ready to run FinSL-signbank on a web server or in a production environment, check out the documentation for instructions at [https://github.com/Signbank/FinSL-signbank/wiki/Install][wiki-install]
Remember to fill in the settings for production in
    
    signbank/settings/production.py

# Translations

FinSL-signbank uses djangos internalization and localization features to make the interface easily translatable to multiple languages.

You can create new locales by running:

    python bin/develop.py makemessages yourlocale

This creates django.po file for the locale you chose. Write your translations inside the quotes msgstr:

    msgstr ""
    For example: msgstr "My translation of the text"

An example of one translated string/text:

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
Remember to restart/refresh your server when doing this to make sure the new translations are in use.

# Contribution

If you want to contribute to the project, contact the repository administrator [@henrinie][admin] or [University of Jyväskylä's Sign language centre][vkk-english].

[requirements.txt]: https://github.com/Signbank/FinSL-signbank/blob/master/requirements.txt
[vkk-english]: http://viittomakielenkeskus.jyu.fi/inenglish.html
[wiki]: https://github.com/Signbank/FinSL-signbank/wiki
[wiki-install]: https://github.com/Signbank/FinSL-signbank/wiki/Install
[auslan-signbank]: https://github.com/Signbank/Auslan-signbank
[ngt-signbank]: https://github.com/Signbank/NGT-signbank
[elan-link]: https://tla.mpi.nl/tools/tla-tools/elan/
[sqlite-link]: https://www.sqlite.org/
[admin]: https://github.com/henrinie
