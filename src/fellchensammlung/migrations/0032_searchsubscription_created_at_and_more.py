# Generated by Django 5.1.4 on 2025-01-01 22:04

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0031_alter_searchsubscription_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchsubscription',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='searchsubscription',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
