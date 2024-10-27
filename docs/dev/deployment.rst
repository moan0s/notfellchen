.. highlight:: none

**********
Deployment
**********

There are different ways to deploy Notfellchen. We support an ansible+docker based deployment and manual installation.

Ansible deployment
==================

Notfellchen can be deployed with the `notfellchen-ansible-role <https://github.com/moan0s/ansible-role-notfellchen>`_ that is based on the
official Notfellchen docker image. This role will only install notfellchen itself. If you want a complete setup that includes a
database and a webserver with minimal configuration you can use the
`mash-playbook <https://github.com/mother-of-all-self-hosting/mash-playbook>`_ by following `it's documentation
on Notfellchen <https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/services/notfellchen.md>`_.



Manual Deployment
=================


This guide describes the installation of a installation of Notfellchen from source. It is inspired by this great guide from
pretix_.

.. warning:: Even though this guide tries to make it as straightforward to run Notfellchen, it still requires some Linux experience to
             get it right. If you're not feeling comfortable managing a Linux server, check out a managed service_.

This guide is tested on **Ubuntu20.04** but it should work very similar on other modern systemd based distributions.

Requirements
------------

Please set up the following systems beforehand, it will not be explained here in detail (but see these links for external
installation guides):

* A SMTP server to send out mails, e.g. `Postfix`_ on your machine or some third-party server you have credentials for
* A HTTP reverse proxy, e.g. `nginx`_ or Traefik to allow HTTPS connections
* A `PostgreSQL`_ database server

Also recommended is, that you use a firewall, although this is not a Notfellchen-specific recommendation. If you're new to
Linux and firewalls, it is recommended that you start with `ufw`_.

.. note:: Please, do not run Notfellchen without HTTPS encryption. You'll handle user data and thanks to `Let's Encrypt`_
          SSL certificates can be obtained for free these days.

Unix user
---------

As we do not want to run notfellchen as root, we first create a new unprivileged user::

    # adduser notfellchen --disabled-password --home /var/notfellchen

In this guide, all code lines prepended with a ``#`` symbol are commands that you need to execute on your server as
``root`` user (e.g. using ``sudo``); all lines prepended with a ``$`` symbol should be run by the unprivileged user.

Database
--------

Having the database server installed, we still need a database and a database user. We can create these with any kind
of database managing tool or directly on our database's shell. Please make sure that UTF8 is used as encoding for the
best compatibility. You can check this with the following command::

    # sudo -u postgres psql -c 'SHOW SERVER_ENCODING'

For PostgreSQL database creation, we would do::

    # sudo -u postgres createuser notfellchen
    # sudo -u postgres createdb -O notfellchen notfellchen
    # su notfellchen
    $ psql
    > ALTER USER notfellchen PASSWORD 'strong_password';

Package dependencies
--------------------

To build and run notfellchen, you will need the following debian packages::

    # apt-get install git build-essential python-dev python3-venv python3 python3-pip \
                      python3-dev

Config file
-----------

We now create a config directory and config file for notfellchen::

    # mkdir /etc/notfellchen
    # touch /etc/notfellchen/notfellchen.cfg
    # chown -R notfellchen:notfellchen /etc/notfellchen/
    # chmod 0600 /etc/notfellchen/notfellchen.cfg

Fill the configuration file ``/etc/notfellchen/notfellchen.cfg`` with the following content (adjusted to your environment)::

    [notfellchen]
    instance_name=My library
    url=https://notfellchen.example.com

    [database]
    backend=postgresql
    name=notfellchen
    user=notfellchen

    [locations]
    static=/var/notfellchen/static

    [mail]
    ; See config file documentation for more options
    ; from=notfellchen@example.com
    ; host=127.0.0.1
    ; user=notfellchen
    ; password=foobar
    ; port=587

    [security]
    ; See https://securitytxt.org/ for reference
    ;Contact=
    ;Expires=
    ;Encryption=
    ;Preferred-Languages=
    ;Scope=
    ;Policy=

Install notfellchen as package
------------------------

Now we will install notfellchen itself. The following steps are to be executed as the ``notfellchen`` user. Before we
actually install notfellchen, we will create a virtual environment to isolate the python packages from your global
python installation::

    $ python3 -m venv /var/notfellchen/venv
    $ source /var/notfellchen/venv/bin/activate
    (venv)$ pip3 install -U pip setuptools wheel

We now clone and install notfellchen, its direct dependencies and gunicorn::

    (venv)$ git clone https://github.com/moan0s/Notfellchen2
    (venv)$ cd Notfellchen2/src/
    (venv)$ pip3 install -r requirements.txt
    (venv)$ pip3 install -e .

Note that you need Python 3.6 or newer. You can find out your Python version using ``python -V``.

Finally, we compile static files and create the database structure::

    (venv)$ ./manage.py collectstatic
    (venv)$ ./manage.py migrate
    (venv)$ django-admin compilemessages --ignore venv


Start notfellchen as a service
-------------------------

You should start notfellchen using systemd to automatically start it after a reboot. Create a file
named ``/etc/systemd/system/notfellchen-web.service`` with the following content::

    [Unit]
    Description=notfellchen web service
    After=network.target

    [Service]
    User=notfellchen
    Group=notfellchen
    Environment="VIRTUAL_ENV=/var/notfellchen/venv"
    Environment="PATH=/var/notfellchen/venv/bin:/usr/local/bin:/usr/bin:/bin"
    ExecStart=/var/notfellchen/venv/bin/gunicorn notfellchen.wsgi \
                          --name notfellchen --workers 5 \
                          --max-requests 1200  --max-requests-jitter 50 \
                          --log-level=info --bind=127.0.0.1:8345
    WorkingDirectory=/var/notfellchen
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target

You can now run the following commands to enable and start the services::

    # systemctl daemon-reload
    # systemctl enable notfellchen-web
    # systemctl start notfellchen-web


SSL
---

The following snippet is an example on how to configure a nginx proxy for notfellchen::

        server {
                listen 80;
                listen [::]:80;

                if ($scheme = http) {
                        return 301 https://$server_name$request_uri;
                }

                #
                listen 443 ssl;
                listen [::]:443 ssl;
                ssl_certificate     /etc/letsencrypt/live/notfellchen.example.com/cert.pem;
                ssl_certificate_key /etc/letsencrypt/live/notfellchen.example.com/privkey.pem;
                ssl_protocols       TLSv1.2 TLSv1.3;
                ssl_ciphers         HIGH:!aNULL:!MD5;


            # Set header
            add_header X-Clacks-Overhead "GNU Terry Pratchett";
            add_header Permissions-Policy interest-cohort=(); #Anti FLoC
            add_header Referrer-Policy same-origin;
            add_header X-Content-Type-Options nosniff;

                server_name notfellchen.example.com;
            location / {
                proxy_pass http://localhost:8345;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto https;
                proxy_set_header Host $http_host;
            }

            location /static/ {
                alias /var/notfellchen/static/;
                access_log off;
                expires 365d;
                add_header Cache-Control "public";
            }
        }


We recommend reading about setting `strong encryption settings`_ for your web server.

Next steps
----------

Yay, you are done! You should now be able to reach notfellchen at https://notfellchen.example.com/

Updates
-------

.. warning:: While we try hard not to break things, **please perform a backup before every upgrade**.

To upgrade to a new notfellchen release, pull the latest code changes and run the following commands::

    $ source /var/notfellchen/venv/bin/activate
    (venv)$ git pull
    (venv)$ pg_dump notfellchen > notfellchen.psql
    (venv)$ python manage.py migrate
    (venv)$ django-admin compilemessages --ignore venv

    # systemctl restart notfellchen-web


.. _Postfix: https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-postfix-as-a-send-only-smtp-server-on-ubuntu-16-04
.. _nginx: https://botleg.com/stories/https-with-lets-encrypt-and-nginx/
.. _Let's Encrypt: https://letsencrypt.org/
.. _MySQL: https://dev.mysql.com/doc/refman/5.7/en/linux-installation-apt-repo.html
.. _PostgreSQL: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-20-04
.. _redis: https://blog.programster.org/debian-8-install-redis-server/
.. _ufw: https://en.wikipedia.org/wiki/Uncomplicated_Firewall
.. _strong encryption settings: https://mozilla.github.io/server-side-tls/ssl-config-generator/
.. _service: hyteck.de/services
.. _pretix: https://docs.pretix.eu/en/latest/admin/installation/manual_smallscale.html

