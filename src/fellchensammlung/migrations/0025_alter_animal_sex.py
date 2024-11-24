# Generated by Django 5.1.1 on 2024-11-21 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fellchensammlung', '0024_alter_animal_sex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='sex',
            field=models.CharField(choices=[('F', 'Weiblich'), ('M', 'Männlich'), ('M_N', 'Männlich, kastriert'), ('F_N', 'Weiblich Kastriert'), ('I', 'Intersex')], max_length=20),
        ),
    ]