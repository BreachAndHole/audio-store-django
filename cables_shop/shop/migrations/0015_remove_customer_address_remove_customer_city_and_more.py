# Generated by Django 4.0.4 on 2022-05-31 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_remove_customer_middle_name_customer_address_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='address',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='city',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='state',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='zipcode',
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200, null=True, verbose_name='адрес')),
                ('city', models.CharField(max_length=50, null=True, verbose_name='город')),
                ('state', models.CharField(max_length=70, null=True, verbose_name='область')),
                ('zipcode', models.CharField(max_length=10, null=True, verbose_name='почтовый индекс')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_address', to='shop.customer', verbose_name='покупатель')),
            ],
        ),
    ]