# Generated by Django 5.1.1 on 2024-10-29 10:44

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0010_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adoptionnotice',
            name='created_at',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Erstellt am'),
        ),
        migrations.AlterField(
            model_name='adoptionnotice',
            name='last_checked',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Zuletzt überprüft am'),
        ),
    ]
