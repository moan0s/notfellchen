# Generated by Django 5.0.6 on 2024-08-02 17:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fellchensammlung", "0002_basenotification_commentnotification"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscriptions",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "adoption_notice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fellchensammlung.adoptionnotice",
                        verbose_name="AdoptionNotice",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Nutzer*in",
                    ),
                ),
            ],
        ),
    ]
