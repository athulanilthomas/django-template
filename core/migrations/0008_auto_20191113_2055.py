# Generated by Django 2.2.6 on 2019-11-13 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20191112_2313'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='refund_granted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='refund_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('PRO', 'Processing'), ('PKD', 'Packed'), ('SHP', 'Shipped'), ('DLV', 'Delivered')], max_length=3, null=True),
        ),
    ]