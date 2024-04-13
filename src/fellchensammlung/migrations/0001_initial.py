# Generated by Django 5.0.3 on 2024-04-13 00:02

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='images')),
                ('alt_text', models.TextField(max_length=2000)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a natural languages name (e.g. English, French, Japanese etc.).', max_length=200, unique=True)),
                ('languagecode', models.CharField(help_text='Enter the language code for this language. For further information see  http://www.i18nguy.com/unicode/language-identifiers.html', max_length=10, verbose_name='Language code')),
            ],
            options={
                'verbose_name': 'Language',
                'verbose_name_plural': 'Languages',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('postcode', models.CharField(max_length=200)),
                ('country', models.CharField(choices=[('DE', 'Germany'), ('AT', 'Austria'), ('CH', 'Switzerland')], max_length=20)),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
            ],
        ),
        migrations.CreateModel(
            name='MarkdownContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Markdown content',
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('rule_text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a animal species', max_length=200, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Species',
                'verbose_name_plural': 'Species',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AdoptionNotice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(default=datetime.datetime.now, verbose_name='Created at')),
                ('searching_since', models.DateField(verbose_name='Searching for a home since')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('further_information', models.URLField(blank=True, null=True, verbose_name='Link to further information')),
                ('group_only', models.BooleanField(default=False, verbose_name='Only group adoption')),
                ('photos', models.ManyToManyField(blank=True, to='fellchensammlung.image')),
            ],
            options={
                'permissions': [('create_active_adoption_notice', 'Can create an active adoption notice')],
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trust_level', models.CharField(choices=[('admin', 'Administrator*in'), ('Moderator', 'Moderator*in'), ('Koordinator*in', 'Koordinator*in'), ('Mitglied', 'Mitglied')], default='Mitglied', max_length=100)),
                ('preferred_language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='fellchensammlung.language', verbose_name='Preferred language')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Member',
                'verbose_name_plural': 'Members',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='ID dieses reports', primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('action taken', 'Action was taken'), ('no action taken', 'No action was taken'), ('waiting', 'Waiting for moderator action')], max_length=30)),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('adoption_notice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fellchensammlung.adoptionnotice')),
                ('reported_broken_rules', models.ManyToManyField(blank=True, to='fellchensammlung.rule')),
            ],
            options={
                'permissions': [],
            },
        ),
        migrations.CreateModel(
            name='ModerationAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('user_banned', 'User was banned'), ('content_deleted', 'Content was deleted'), ('comment', 'Comment was added'), ('other_action_taken', 'Other action was taken'), ('no_action_taken', 'No action was taken')], max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('public_comment', models.TextField(blank=True)),
                ('private_comment', models.TextField(blank=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fellchensammlung.report')),
            ],
        ),
        migrations.CreateModel(
            name='RescueOrganization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('trusted', models.BooleanField(default=False, verbose_name='Trusted')),
                ('instagram', models.URLField(blank=True, null=True, verbose_name='Instagram profile')),
                ('facebook', models.URLField(blank=True, null=True, verbose_name='Facebook profile')),
                ('fediverse_profile', models.URLField(blank=True, null=True, verbose_name='Fediverse profile')),
                ('website', models.URLField(blank=True, null=True, verbose_name='Website')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='fellchensammlung.location')),
            ],
        ),
        migrations.AddField(
            model_name='adoptionnotice',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fellchensammlung.rescueorganization', verbose_name='Organization'),
        ),
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_birth', models.DateField(verbose_name='Date of birth')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('sex', models.CharField(choices=[('M_N', 'neutered male'), ('M', 'male'), ('F_N', 'neutered female'), ('F', 'female')], max_length=20)),
                ('adoption_notice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fellchensammlung.adoptionnotice')),
                ('photos', models.ManyToManyField(blank=True, to='fellchensammlung.image')),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='fellchensammlung.species')),
            ],
        ),
    ]
