# Generated by Django 5.1.1 on 2024-11-14 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0020_alter_rescueorganization_internal_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reason_for_signup',
            field=models.TextField(default='-', verbose_name='Grund für die Registrierung'),
            preserve_default=False,
        ),
    ]