# Generated by Django 3.0.6 on 2020-05-25 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InjectionLog', '0003_auto_20200525_0056'),
    ]

    operations = [
        migrations.AddField(
            model_name='cats',
            name='fip_type',
            field=models.CharField(default='dry', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cats',
            name='neuro',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cats',
            name='ocular',
            field=models.BooleanField(default=False),
        ),
    ]
