*****************
API Documentation
*****************

The Notfellchen API serves the purpose of supporting 3rd-person applications, whether you want to display data in a custom format or add data from other sources.

.. warning::
    The current API is limited in it's functionality. I you miss a specific feature please contact the developers!

API Access
==========

Via browser
-----------

When a user is logged in, they can easily access the API in their browser, authenticated by their session.
The API endpoint can be found at http://notfellchen.org/api/adoption_notices

Via token
---------


All users are able to generate a token that allows them to use the API. This can be done in the user's profile.
An application can then send this token in the request header for authorization.

.. code-block::
    $ curl -X GET http://notfellchen.org/api/adoption_notice -H 'Authorization: Token 49b39856955dc6e5cc04365498d4ad30ea3aed78'


.. warning::
    Usage or creation of content still has to follow the terms of Notfellchen.org
    Copyright of content is often held by rescue organizations, so you are not allowed to simply mirror content.
    Talk to the Notfellchen-Team if you want develop such things.


Endpoints
---------

All Endpoints are documented at  https://notfellchen.org/api/schema/swagger-ui/ or at https://notfellchen.org/api/schema/redoc/ if you prefer redoc.
The OpenAI schema can be downloaded at https://notfellchen.org/api/schema/

Examples are documented here.

Get Adoption Notices
++++++++++++++++++++

.. code-block::
    curl --request GET \
  --url https://notfellchen.org/api/adoption_notice \
  --header 'Authorization: {{token}}'

Create Adoption Notice
++++++++++++++++++++++

.. code-block::
    curl --request POST \
  --url https://notfellchen.org/api/adoption_notice \
  --header 'Authorization: {{token}}' \
  --header 'content-type: multipart/form-data' \
  --form name=TestAdoption1 \
  --form searching_since=2024-11-19 \
  --form 'description=Lorem ipsum **dolor sit** amet' \
  --form further_information=https://notfellchen.org \
  --form location_string=Berlin \
  --form group_only=true

Add Animal to Adoption Notice
+++++++++++++++++++++++++++++

.. code-block::
    curl --request POST \
      --url https://notfellchen.org/api/animals/ \
      --header 'Authorization: {{token}}' \
      --header 'content-type: multipart/form-data' \
      --form name=TestAnimal1 \
      --form date_of_birth=2024-11-19 \
      --form 'description=Lorem animal **dolor sit**.' \
      --form sex=F \
      --form species=1 \
      --form adoption_notice=1

Add picture to Animal or Adoption Notice
++++++++++++++++++++++++++++++++++++++++

.. code-block::
    curl -X POST https://notfellchen.org/api/images/ \
    -H "Authorization: Token {{token}}" \
    -F "image=@256-256-crop.jpg" \
    -F "alt_text=Puppy enjoying the sunshine" \
    -F "attach_to_type=animal" \
    -F "attach_to=48

Species
+++++++

Getting available species is mainly important when creating animals

.. code-block::
    curl --request GET \
      --url https://notfellchen.org/api/species \
      --header 'Authorization: {{token}}'
