# Generated by Django 2.2.6 on 2019-11-10 15:03

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_order_billing_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaddress',
            name='country',
            field=django_countries.fields.CountryField(max_length=2),
        ),
    ]
