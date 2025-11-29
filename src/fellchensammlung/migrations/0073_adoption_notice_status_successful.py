import logging

from django.db import migrations


def migrate_status(apps, schema_editor):
    # We can't import the model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    AdoptionNotice = apps.get_model("fellchensammlung", "AdoptionNotice")
    for adoption_notice in AdoptionNotice.objects.filter(
            adoption_notice_status__in=("closed_successful_without_notfellchen", "closed_successful_with_notfellchen")):
        adoption_notice.adoption_notice_status = "closed_successfully"
        adoption_notice.save()


class Migration(migrations.Migration):
    dependencies = [
        ('fellchensammlung', '0072_alter_adoptionnotice_adoption_notice_status_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_status),
    ]
