# Generated by Django 3.0.6 on 2021-01-16 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InjectionLog', '0039_fixtimezone_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='cats',
            name='bad',
            field=models.BooleanField(default=False),
        ),
    ]
