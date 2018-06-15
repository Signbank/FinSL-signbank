.. _installation:

============
Installation
============

*Updated on June 15th 2018 by* `@henrinie`_

.. _@henrinie: https://github.com/henrinie

These instructions are written for linux operating systems. For Windows or MacOS
some parts might be relevant, look up `python docs`_ and `django docs`_ for
further instructions for those operating systems.

.. _python docs: https://docs.python.org/3/index.html
.. _django docs: https://docs.djangoproject.com/en/stable/

Set up the environment
-----------------------

Clone the git repository, create a python virtual environment, install
dependencies with pip, and configure the relevant settings.

Git repository
^^^^^^^^^^^^^^

Clone the repository to your machine from GitHub:

.. code-block:: bash

    $ git clone https://github.com/Signbank/FinSL-signbank.git


Python Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a
`virtual environment in python3 <https://docs.python.org/3/library/venv.html>`_:

.. code-block:: bash

    $ cd FinSL-signbank
    $ python3 -m venv venv
    $ source venv/bin/activate

If you need to deactivate the environment write:

.. code-block:: bash

    $ deactivate

Install dependencies with pip
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install required python dependencies:

.. code-block:: bash

    $ pip install -r /path/to/requirements.txt
    Example: $ pip install -r FinSL-signbank/requirements.txt

Configure settings
^^^^^^^^^^^^^^^^^^

Edit settings files in FinSL-signbank/signbank/settings/ and change the paths
in:

.. code-block:: python

    # settings/production.py & settings/development.py
    LOCALE_PATHS = (
        '/path/to/FinSL-signbank/locale',
    )
    STATIC_ROOT = '/path/to/FinSL-signbank/static' # For development only! Production dir needs to be server by web server.
    MEDIA_ROOT = '/path/to/FinSL-signbank/media' # For development only! Production dir needs to be server by web server.


.. code-block:: python

    # settings/development.py
    LOGGING = {
    ...
    'filename': '/path/you/want/debug.log'
    ...
    }


.. code-block:: python

    # settings/production.py

    # IMPORTANT: The hostname that this signbank runs on, this prevents HTTP Host header attacks
    ALLOWED_HOSTS = ['yourhost.here.com']

    STATIC_ROOT = '/path/to/static' # Served by the web server, e.g. /var/www/yourdomain/static
    MEDIA_ROOT = '/path/to/media' # Served by the web server, e.g. /var/www/yourdomain/media

    WSGI_FILE = '/path/to/FinSL-signbank/signbank/wsgi.py' # This will matter when you want to use a web server

Rename settings/settings_secret.py.template

.. code-block:: bash

    $ mv settings/settings_secret.py.template settings/settings_secret.py

Edit settings/settings_secret.py

.. code-block:: python

    # settings/settings_secret.py

    # Make SECRET_KEY unique and do not share it with anyone
    # You may use characters available in ASCII
    SECRET_KEY = 'yoursecretkey!"#¤%&/()=?'
    ADMINS = (
        ('Your Name', 'your.email@address.com'),
    )
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/path/to/signbank.db',
        }
    }

.. tip::
    Generate
    `a random secret key <http://www.miniwebtool.com/django-secret-key-generator/>`_


Databases
---------

We kindly recommend using PostgreSQL with FinSL-signbank, because
django-framework is optimized to run on PostgreSQL. We have used MySQL in the
past, but at least in our case we started to experience some problems with
migrations.

PostgreSQL
^^^^^^^^^^

When you are ready to switch to a database server, PostgreSQL is our
recommendation, see django docs for more information about setting django up
with PostgreSQL:
`<https://docs.djangoproject.com/en/stable/ref/databases/#postgresql-notes>`_.

In your postgresql.conf make sure you have the following:

.. code-block:: psql

    client_encoding = 'UTF8'
    default_transaction_isolation = 'read committed'
    timezone: 'UTC' # Because USE_TZ = True in FinSL-signbank


Edit settings/secret_settings.py

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'mydatabase',
            'USER': 'mydatabaseuser',
            'PASSWORD': 'mypassword',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

Then install psycopg2 with pip when your virtual environment is activated.

.. code-block:: bash

    $ pip install psycopg2

SQLite
^^^^^^

Edit the following lines in settings/secret_settings.py:

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/path/to/signbank.db',
        }
    }

MySQL
^^^^^

If your database of choice is
`MySQL <https://docs.djangoproject.com/en/stable/ref/databases/#mysql-notes>`_,
create my.cnf for your MySQL credentials

.. code-block:: bash

    [client]
    database = yourdatabasename
    user = yourusername
    password = "yourpassword"
    host = host.name.com # Could be localhost, if the database is hosted on the local machine
    port = 3306 # Or whichever is the correct one for your setting
    default-character-set = utf8 # This is pretty much required with django

After done with my.cnf settings, make sure that the file is not accessible by
anyone else than you

.. code-block:: bash

    $ chmod 600 my.cnf

If you have problems with access by apache, place your my.cnf in a place where
it can be accessed, or play with the user rights in the current location.

Edit settings/secret_settings.py

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {
                'read_default_file': '/path/to/my.cnf',
                'init_command': 'SET storage_engine=INNODB',
            },
        }
    }

Then install MySQL-python with pip when your virtual environment is activated.

.. code-block:: bash

    $ pip install MySQL-python

On RHEL and CentOS you might need additional packages, if the pip installing
of MySQL-python is not working, you might try to install mariadb-devel. For
debian based distributions the package name might be different.

.. code-block:: bash

    $ sudo yum install mariadb-devel

It might be required that you install MySQL-python again with pip. Remove it
and install it again without using the cache.

.. code-block:: bash

    $ pip uninstall MySQL-python
    $ pip install MySQL-python --no-cache

Other settings
--------------

Change these settings in settings/base.py according to your needs

.. code-block:: python

    # settings/base.py
    TIME_ZONE = 'Europe/Helsinki'
    LANGUAGE_CODE = 'fi' # examples: 'en-us', 'de', 'se'

    # Enter the desired languages under this setting. These languages can be translated in the app.
    LANGUAGES = (
        ('fi', _('Finnish')),
        ('en', _('English')),
    )


Django debug toolbar
^^^^^^^^^^^^^^^^^^^^

Using django debug toolbar is optional, but recommended as it is very useful
for evaluating of the actual SQL queries for example.

To install django debug toolbar (while your virtual environment is active):

.. code-block:: bash

    $ pip install django-debug-toolbar

If you don't want to use django debug toolbar, remove or comment out the
following lines in settings/development.py:

.. code-block:: python

    if DEBUG:
        # Setting up debug toolbar.
        MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
        INSTALLED_APPS += ('debug_toolbar',)

and also remove or comment out the following lines in signbank/urls.py:

.. code-block:: python

    if settings.DEBUG:
        import debug_toolbar
        from django.conf.urls.static import static
        # Add debug_toolbar when DEBUG=True, also add static+media folders when in development.
        # DEBUG should be False when in production!
        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
            + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

Database migration
------------------

Once we have handled all the settings, we can migrate the database.

Make sure you are in your environment

.. code-block:: bash

    $ source /path/to/venv/bin/activate

First create migrations for django flatpages app to add translation fields with
django-modeltranslation:

.. code-block:: bash

    $ python FinSL-signbank/bin/develop.py makemigrations

Then migrate:

.. code-block:: bash

    $ python FinSL-signbank/bin/develop.py migrate

Load fixture for flatpages:

.. code-block:: bash

    $ python FinSL-signbank/bin/develop.py loaddata flatpages_initial_data

*Note: In MySQL you might need to change the default collation, if the
utf8_general_ci doesn't match your languages alphabetical order. You might
need to do this to all the tables of the signbank app (not on the ones that
begin with django_ or auth_).*
*Take a look at:*
`<http://dev.mysql.com/doc/refman/5.7/en/charset-unicode-sets.html>`_ and
`<https://docs.djangoproject.com/en/stable/ref/databases/#collation-settings>`_

.. _mysql charset:
.. _django collation:

Run djangos test/development server to see if it works

.. code-block:: bash

    # Run locally, only accessible from the machine you are running signbank with
    $ python FinSL-signbank/bin/develop.py runserver localhost:8000

    # Or run in your network/internet by entering your IPaddress or your hostname
    $ python FinSL-signbank/bin/develop.py runserver 80.12.16.10:8000 # Change the port if needed


Apache (httpd)
--------------

Apache + mod_wsgi
^^^^^^^^^^^^^^^^^

This process can differ between linux distributions. Take a look at `django documentation`_.

You can read about the settings in `django documentation`_.
These settings work with CentOS7 and apache httpd 2.4. The location of the
configurations vary between linux distributions. It is important to note that
you should definitely store FinSL-signbank and django files outside of the path
your webserver serves to the web (f.ex. /var/www/), I suggest that you store
the files inside your /home/ folder. This way you avoid the risk of your
settings, code and files being accessible from the web. Your wsgi.py file
should be located at FinSL-signbank/signbank/wsgi.py.

.. _django documentation: https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/

.. code-block:: bash

    #/etc/httpd/conf/httpd.conf
    # These lines set the WSGI directories for FinSL-signbank and django
    WSGIScriptAlias / /path/to/FinSL-signbank/signbank/wsgi.py
    WSGIDaemonProcess FinSL-signbank python-path=/path/to/FinSL-signbank:/path/to/FinSL-signbank/venv/lib/python3.x/site-packages
    WSGIProcessGroup FinSL-signbank

    <Directory /path/to/FinSL-signbank/signbank>
        SetEnvIfNoCase Host your\.domain\.com VALID_HOST
        Require env VALID_HOST
        Options +FollowSymLinks -ExecCGI
        <Files wsgi.py>
            Require env VALID_HOST
        </Files>
    </Directory>

    # Creates alias for /media as /static
    # This will be the directory where static files are collected to, the web server should serve them not django.
    Alias /static /path/to/static # For example /var/www/yourdomain/static ,
    # Sets robots.txt to be accessible at /robots.txt, you need to create the robots.txt file to suit your needs
    Alias /robots.txt /path/to/static/robots.txt
    # Sets favicon.ico to be accessible at /favicon.ico, you need to create a favicon
    Alias /favicon.ico /path/to/FinSL-signbank/favicon.ico

    # Create alias for /media/ directory
    Alias /media /path/to/media # For example /var/www/yourdomain/media
    # Gives access to /media directory
    <Directory /path/to/media>
        SetEnvIfNoCase Host your\.domain\.com VALID_HOST
        Require env VALID_HOST
    </Directory>


Apache envvars
^^^^^^^^^^^^^^

If you are running Signbank with apache (or probably any web server), make sure
it is running on the right locale. For example in CentOS Apache seemed to run
on LANG=C by default. To avoid problems with non-ascii characters,
add these values to your web server evnvvars (in CentOS /etc/sysconfig/httpd):

.. code-block:: bash

    LANG='en_US.UTF-8'
    LC_ALL='en_US.UTF-8'


HTTPS
^^^^^

It is strongly recommended that you run your production server with HTTPS.
For this take a look at the HTTPS specific settings in the settings files.
Have a look at the django docs:
`<https://docs.djangoproject.com/en/stable/topics/security/#ssl-https>`_
And also configure your domain properly for HTTPS. If you need free
certificates check out LetsEncrypt at `<https://letsencrypt.org/>`_.
