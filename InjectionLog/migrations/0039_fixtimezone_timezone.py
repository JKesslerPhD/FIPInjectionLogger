# Generated by Django 3.0.6 on 2020-10-31 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InjectionLog', '0038_fixtimezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='fixtimezone',
            name='timezone',
            field=models.CharField(default='UTC', max_length=64),
        ),
    ]
