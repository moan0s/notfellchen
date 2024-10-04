# Generated by Django 5.1.1 on 2024-09-28 20:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0004_rename_created_by_adoptionnotice_owner_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rescueorganization',
            name='allows_using_materials',
            field=models.CharField(choices=[('allowed', 'Usage allowed'), ('requested', 'Usage requested'), ('denied', 'Usage denied'), ('other', "It's complicated"), ('not_asked', 'Not asked')], default='Not asked', max_length=200, verbose_name='Erlaubt Nutzung von Inhalten'),
        ),
        migrations.AlterField(
            model_name='rescueorganization',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='fellchensammlung.location'),
        ),
    ]