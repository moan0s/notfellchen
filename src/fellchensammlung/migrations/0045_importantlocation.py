# Generated by Django 5.1.4 on 2025-04-27 11:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0044_alter_location_place_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportantLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=200)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fellchensammlung.location')),
            ],
        ),
    ]
