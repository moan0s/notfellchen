Translation
===========
Translate HTML-files
____________________
First you have to add the text "{% load i18n %}" in every html file at the top.

Write the string in your html file between these two tags: {% translate "String" %}

Translate python-files
______________________
The underscore markes the string for translation. e.g. _("String")


Workflow
_________
- Generate the messages with the command: "django-admin makemessages -l de --ignore venv" de stands in this example for german
- Translate the strings in the file src/local/de/LC_MESSAGES/django.po
- Convert the strings for django with the command: "django-admin compilemessages --ignore venv"  
