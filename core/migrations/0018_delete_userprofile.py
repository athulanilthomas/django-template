# Generated by Django 2.2.6 on 2019-11-20 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_userprofile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]