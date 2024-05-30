# Generated by Django 5.0.6 on 2024-06-04 06:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fellchensammlung", "0002_comment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="report",
            name="adoption_notice",
        ),
        migrations.RenameField(
            model_name="report",
            old_name="comment",
            new_name="user_comment",
        ),
        migrations.CreateModel(
            name="ReportComment",
            fields=[
                (
                    "report_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="fellchensammlung.report",
                    ),
                ),
                (
                    "reported_comment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fellchensammlung.comment",
                    ),
                ),
            ],
            bases=("fellchensammlung.report",),
        ),
        migrations.CreateModel(
            name="ReportAdoptionNotice",
            fields=[
                (
                    "report_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="fellchensammlung.report",
                    ),
                ),
                (
                    "adoption_notice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fellchensammlung.adoptionnotice",
                    ),
                ),
            ],
            bases=("fellchensammlung.report",),
        ),
    ]
