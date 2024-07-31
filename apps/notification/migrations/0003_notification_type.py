# Generated by Django 5.0.4 on 2024-07-31 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_alter_notification_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('special', 'Special'), ('general', 'General'), ('payment', 'Payment'), ('update', 'Update')], default='general', max_length=10),
            preserve_default=False,
        ),
    ]
