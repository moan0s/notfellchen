# Generated by Django 5.1.4 on 2025-04-24 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0041_location_city_location_country_location_housenumber_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='county',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
