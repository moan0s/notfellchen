# Generated by Django 5.1.4 on 2025-04-06 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0040_alter_rescueorganization_allows_using_materials'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='city',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='country',
            field=models.CharField(blank=True, help_text='Standardisierter Ländercode nach ISO 3166-1 ALPHA-2', max_length=2, null=True, verbose_name='Ländercode'),
        ),
        migrations.AddField(
            model_name='location',
            name='housenumber',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='postcode',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='street',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='rescueorganization',
            unique_together={('external_object_identifier', 'external_source_identifier')},
        ),
    ]
