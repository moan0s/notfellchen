# Generated by Django 5.1.4 on 2025-01-14 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0036_basenotification_read_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basenotification',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Titel'),
        ),
    ]
