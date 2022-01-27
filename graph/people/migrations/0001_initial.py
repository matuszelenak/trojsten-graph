# Generated by Django 4.0.1 on 2022-01-26 11:50

import django.contrib.auth.validators
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import people.models
import people.utils.variable_res_date


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('maiden_name', models.CharField(blank=True, max_length=128, null=True)),
                ('nickname', models.CharField(blank=True, max_length=128, null=True)),
                ('gender', models.IntegerField(choices=[(1, 'Male'), (2, 'Female'), (3, 'Other')], default=3)),
                ('birth_date', people.utils.variable_res_date.VariableResolutionDateField(blank=True, null=True)),
                ('death_date', people.utils.variable_res_date.VariableResolutionDateField(blank=True, null=True)),
                ('visible', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'person',
                'verbose_name_plural': 'people',
                'ordering': ('-birth_date',),
                'unique_together': {('first_name', 'last_name', 'nickname')},
            },
            managers=[
                ('objects', people.models.PersonManager()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.IntegerField(choices=[(1, 'Elementary school'), (2, 'High school'), (3, 'University'), (4, 'Seminar'), (5, 'Other')])),
                ('name', models.CharField(max_length=256, unique=True)),
                ('visible', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='people.group')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_started', people.utils.variable_res_date.VariableResolutionDateField(blank=True, null=True)),
                ('date_ended', people.utils.variable_res_date.VariableResolutionDateField(blank=True, null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='people.group')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date_started',),
                'unique_together': {('person', 'group')},
            },
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relationships_as_first', to=settings.AUTH_USER_MODEL)),
                ('second_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relationships_as_second', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('first_person', 'second_person')},
            },
        ),
        migrations.CreateModel(
            name='RelationshipStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Blood relatives'), (2, 'Siblings'), (3, 'Parent-child'), (4, 'Married'), (5, 'Engaged'), (6, 'Dating'), (7, 'Rumour')])),
                ('date_start', people.utils.variable_res_date.VariableResolutionDateField(blank=True, null=True)),
                ('date_end', people.utils.variable_res_date.VariableResolutionDateField(blank=True, null=True)),
                ('confirmed_by', models.IntegerField(choices=[(0, 'Awaiting approval from both people in the relationship'), (1, 'Confirmed by the first person'), (2, 'Confirmed by the second person'), (3, 'Confirmed by both people')], default=0)),
                ('visible', models.BooleanField(default=True)),
                ('relationship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to='people.relationship')),
            ],
            options={
                'verbose_name_plural': 'relationship statuses',
                'ordering': ('-date_start',),
                'get_latest_by': ('date_end', 'date_start'),
            },
        ),
        migrations.CreateModel(
            name='RelationshipStatusNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('type', models.IntegerField(choices=[(1, 'Public note'), (2, 'Private note')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('reason', models.IntegerField(choices=[(1, 'Note on relationship start'), (2, 'Note on relationship end'), (3, 'Unspecified reason')])),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='people.relationshipstatus')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('type', models.IntegerField(choices=[(1, 'Public note'), (2, 'Private note')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GroupMembershipNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('type', models.IntegerField(choices=[(1, 'Public note'), (2, 'Private note')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('membership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='people.groupmembership')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
