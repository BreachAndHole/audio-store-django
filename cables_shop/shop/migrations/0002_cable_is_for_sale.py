# Generated by Django 4.0.4 on 2022-06-09 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cable',
            name='is_for_sale',
            field=models.BooleanField(default=True, verbose_name='в продаже'),
        ),
    ]