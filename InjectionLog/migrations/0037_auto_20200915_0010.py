# Generated by Django 3.0.6 on 2020-09-15 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InjectionLog', '0036_auto_20200914_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergs',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usergs',
            name='brand',
            field=models.CharField(max_length=100),
        ),
    ]