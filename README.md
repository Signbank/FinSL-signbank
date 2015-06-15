# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* **Quick summary**
    * This repository is for Finnish Signbank - a sign language Gloss database.
    * Finnish Signbank is a fork of Dutch Signbank (https://github.com/Woseseltops/signbank).
    * Finnish version of Signbank is intended for research use at first, and perhaps later it will be opened to public use.
    * The source code is free to use and you can build your own version of Signbank on top of it.
    * This version of Signbank is the first one to offer Django's translation engine feature, so it should be fairly easy to translate to different languages.
    * Signbank is built on django-framework and it uses python 2.7.

* **Version**

Signbank-fi is not yet released and it is still under development.
Once the first working version of Signbank-fi is working, the repository will be made public.

### How do I get set up? ###

* **Summary of set up**

> pip install -r /path/to/requirements.txt
> python bin/develop.py migrate
> python bin/develop.py runserver 127.0.0.1:8000

* **Configuration**

Before you can get Signbank-fi working, you must change some paths in:  
> signbank/settings/base.py  
> signbank/settings/development.py                              

* **Dependencies**

> See *requirements.txt*

* **Database configuration**

Django should make all the needed database configurations apart from setting up a database.
> bin/develop.py migrate

* **How to run tests**

Sadly tests are not yet available.

* **Deployment instructions**

### Contribution guidelines ###

Right now this repository is not up for contribution, because this might not be actively maintained. You can fork this and make your own version.

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* **Repo owner or admin**

Henri Nieminen, owner of this repository

* **Other community or team contact**

University of Jyväskylä, Sign language center (http://viittomakielenkeskus.jyu.fi/inenglish.html)