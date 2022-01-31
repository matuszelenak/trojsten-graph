# Generated by Django 4.0.1 on 2022-01-28 19:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegalGuardianship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guarded', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guarded_by', to=settings.AUTH_USER_MODEL)),
                ('guardian', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guardings_of', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]