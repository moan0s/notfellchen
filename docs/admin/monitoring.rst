Monitoring
==========

Notfellchen should, like every other software, be easy to monitor. Therefore a basic metrics are exposed to `https://notfellchen.org/metrics`.
The data is encoded in JSON format and is therefore suitable to bea read by humans and it is easy to use it as data source for further processing.


Exposed Metrics
---------------

.. code::

   users: number of users (all roles combined)
   staff: number of users with staff status
   adoption_notices: number of adoption notices
   adoption_notices_by_status: number of adoption notices by major status
   adoption_notices_without_location: number of location notices that are not geocoded

Example workflow
----------------

To use the exposed metrics you will usually need a time series database and a visualization tool.

As time series database we will utilize InfluxDB, the visualization tool will be Grafana.

InfluxDB and Telegraf
^^^^^^^^^^^^^^^^^^^^^

First we install InfluxDB (e.g. with docker, be aware of the security risks!).

.. code::

   # Pull the image
   $ sudo docker pull influxdb

   # Start influxdb
   $ sudo docker run -d -p 8086:8086 -v influxdb:/var/lib/influxdb --name influxdb influxdb

   # Start influxdb console
   $ docker exec -it influxdb influx
   Connected to http://localhost:8086 version 1.8.3
   InfluxDB shell version: 1.8.3
   > create database monitoring
   > create user "telegraf" with password 'mypassword'
   > grant all on monitoring to telegraf

.. note::
   When creating the user telegraf check the double and single quotes for username an password.

Now install telegraf and configure `etc/telegraf/telegraf.conf`. Modify the domain and your password for the InfluxDB database. 

.. literalinclude:: example.telegraf.conf
    :linenos:
    :language: python

Graphana
^^^^^^^^

Now we can simply use the InfluxDB as data source in Grafana and configure until you have
beautiful plots!

.. image:: monitoring_grafana.png

Healthchecks
------------

You can configure notfellchen to give a hourly ping to a healthchecks server. If this ping is not received, you will get notified and cna check why the celery jobs are no running.
Add the following to your `notfellchen.cfg` and adjust the URL to match your check.
.. code::

  [monitoring]
  healthchecks_url=https://health.example.org/ping/5fa7c9b2-753a-4cb3-bcc9-f982f5bc68e8
