# Generated by Django 2.2.6 on 2019-11-13 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20191113_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ref_code',
            field=models.CharField(default='s5d6fs5df5', max_length=20),
            preserve_default=False,
        ),
    ]