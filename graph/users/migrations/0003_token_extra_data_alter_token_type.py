# Generated by Django 4.0.1 on 2022-04-23 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_token_type_alter_token_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='extra_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='token',
            name='type',
            field=models.IntegerField(choices=[(1, 'Account activation'), (2, 'Password reset'), (3, 'Auth token'), (4, 'Email change')], default=1, verbose_name='type'),
        ),
    ]
