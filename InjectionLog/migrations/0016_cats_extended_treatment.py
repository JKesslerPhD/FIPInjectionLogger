# Generated by Django 3.0.6 on 2020-05-27 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InjectionLog', '0015_auto_20200527_0357'),
    ]

    operations = [
        migrations.AddField(
            model_name='cats',
            name='extended_treatment',
            field=models.IntegerField(null=True),
        ),
    ]
