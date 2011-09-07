Requirements
------------

 - Django 1.3 (http://www.djangoproject.com/)
 - Python 2.x (2.6+) (http://www.python.org/)
 - Any Django supported database (http://docs.djangoproject.com/en/dev/ref/databases/)
 - recaptcha-client 1.0.5 or higher (http://pypi.python.org/pypi/recaptcha-client)
 - django-bbmarkup (http://bitbucket.org/offline/django-bbmarkup)


 - RabbitMQ, Broker for Celery (http://jazstudios.blogspot.com/2010/11/setup-django-rabbitmq-and-celery.html)
 - Celery integration for Django 2.3.3 (https://github.com/ask/django-celery)
 - Reversion integration for Django 1.5 (https://github.com/etianen/django-reversion)
 - Form utils integration for Django 0.2.0
 - Networkx 1.5
 - cjson for Python 1.0.5


Installation
------------

    $ pip install Django
    $ pip install recaptcha-client

For SQLite:

    $ pip install pysqlite

For mySQL, install development libraries first (if mysql_config is missing):

    $ sudo apt-get install libmysqlclient-dev

Then install the bindings themselves:

    $ pip install MySQL-python

Installation instructions for django-bbmarkup:

    ln -s `pwd`/bbmarkup ~/.virtualenv/nuspic/lib/pythonX.Y/site-packages


for Network/Simulation
--------------
primary
    # For Django
    $ pip install django-form-utils
    $ pip install django-reversion

    $ pip install python-cjson
    $ pip install networkx

    # For Django-celery
    $ sudo apt-get install rabbitmq-server
    $ pip install django-celery

optional (useful for developer)
    $ pip install django-extensions #(0.6)
    $ pip install django-evolution #(0.6.5)
    $ pip install django-debug-toolbar # (0.8.5)


Synchronizing multiple databases
------------
 
insert DATABASE_ROUTERS in settings
 
for default database
    $ ./manage.py sqlall reversion | ./manage.py dbshell
    $ ./manage.py syncdb
 
for network database
    $ ./manage.py sqlall auth | ./manage.py dbshell --database=network
    $ ./manage.py sqlall django_evolution | ./manage.py dbshell --database=network
    $ ./manage.py syncdb --database=network

for simulation database
    $ ./manage.py sqlall auth | ./manage.py dbshell --database=simulation
    $ ./manage.py sqlall django_evolution | ./manage.py dbshell --database=simulation
    $ ./manage.py sqlall network | ./manage.py dbshell --database=simulation
    $ ./manage.py syncdb --database=simulation


Starting Celery integration for Django
------------
 
    $./manage.py celeryd -E
    $./manage.py celerycam
    $./manage.py celeryev


License
-------

Unless otherwise specified in the source code, the use and redistribution of
the software in this repository are subject to MIT License.

Copyright (C) 2011 onwards by nuSPIC Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

lib/decorators.py: (c) 2006-2009 Alexander Solovyov, new BSD License
