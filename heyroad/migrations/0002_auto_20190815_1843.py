# Generated by Django 2.2.4 on 2019-08-15 16:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heyroad', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='route',
            name='time',
        ),
        migrations.RemoveField(
            model_name='stats',
            name='total_time',
        ),
        migrations.AddField(
            model_name='route',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(seconds=1200)),
        ),
        migrations.AddField(
            model_name='stats',
            name='total_duration',
            field=models.DurationField(default=datetime.timedelta(seconds=1200)),
        ),
    ]
