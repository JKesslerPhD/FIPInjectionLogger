# Generated by Django 3.0.6 on 2020-09-14 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InjectionLog', '0035_auto_20200720_2327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='injectionlog',
            name='gs_brand',
            field=models.CharField(max_length=100, null=True),
        ),
    ]