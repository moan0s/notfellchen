*****************
API Documentation
*****************

The Notfellchen API serves the purpose of supporting 3rd-person applications and anything you can think of basically.

.. warning::
    The current API is limited in it's functionality. I you miss a specific feature please contact the developer!

API Access
==========

Via browser
-----------

When a user is logged in, they can easily access the API in their browser, authenticated by their session.
The API endpoint can be found at /library/api/
http://notfellchen.org/

Via token
---------


All users are able to generate a token that allows them to use the API. This can be done in the user's profile.
An application can then send this token in the request header for authorization.

.. code-block::
    $ curl -X GET http://notfellchen.org/api/adoption_notice -H 'Authorization: Token 49b39856955dc6e5cc04365498d4ad30ea3aed78'

Endpoints
---------

Get Adoption Notices
++++++++++++++++++++

.. code-block::
    curl --request GET \
  --url http://localhost:8000/api/adoption_notice \
  --header 'Authorization: {{token}}'

Create Adoption Notice
++++++++++++++++++++++

.. code-block::
    curl --request POST \
  --url http://localhost:8000/api/adoption_notice \
  --header 'Authorization: {{token}}' \
  --header 'content-type: multipart/form-data' \
  --form name=TestAdoption1 \
  --form searching_since=2024-11-19 \
  --form 'description=Lorem ipsum **dolor sit** amet' \
  --form further_information=https://notfellchen.org \
  --form location_string=Berlin \
  --form group_only=true