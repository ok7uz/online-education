# Generated by Django 5.0.4 on 2024-07-31 06:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_config_value'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Config',
        ),
    ]
