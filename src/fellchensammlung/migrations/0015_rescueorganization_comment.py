# Generated by Django 5.1.1 on 2024-11-09 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0014_rescueorganization_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='rescueorganization',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Kommentar'),
        ),
    ]
