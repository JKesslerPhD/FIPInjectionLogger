# Generated by Django 3.0.6 on 2020-05-25 18:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InjectionLog', '0010_auto_20200525_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cats',
            name='birthday',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='cats',
            name='treatment_start',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='injectionlog',
            name='date_added',
            field=models.DateField(default=datetime.date.today, editable=False),
        ),
    ]
