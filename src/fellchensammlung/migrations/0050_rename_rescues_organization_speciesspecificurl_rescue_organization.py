# Generated by Django 5.2.1 on 2025-06-20 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0049_rescueorganization_exclude_from_check'),
    ]

    operations = [
        migrations.RenameField(
            model_name='speciesspecificurl',
            old_name='rescues_organization',
            new_name='rescue_organization',
        ),
    ]
