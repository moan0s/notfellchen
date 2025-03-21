# Generated by Django 5.1.4 on 2024-12-31 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0028_searchsubscription'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AndoptionNoticeNotification',
            new_name='AdoptionNoticeNotification',
        ),
        migrations.AlterField(
            model_name='searchsubscription',
            name='sex',
            field=models.CharField(choices=[('F', 'Weiblich'), ('M', 'Männlich'), ('M_N', 'Männlich, kastriert'), ('F_N', 'Weiblich Kastriert'), ('I', 'Intergeschlechtlich'), ('A', 'Alle')], max_length=20),
        ),
    ]
