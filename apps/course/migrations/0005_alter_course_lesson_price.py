# Generated by Django 5.0.4 on 2024-07-24 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_partenrollment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='lesson_price',
            field=models.PositiveIntegerField(null=True, verbose_name='lesson price'),
        ),
    ]
