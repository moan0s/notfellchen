# Generated by Django 5.0.3 on 2024-04-14 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fellchensammlung", "0003_alter_text_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="text",
            options={"verbose_name": "Text", "verbose_name_plural": "Texte"},
        ),
    ]