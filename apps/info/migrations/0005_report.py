# Generated by Django 5.0.4 on 2024-08-01 12:08

import config.utils
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_alter_category_options_alter_enrollment_options_and_more'),
        ('info', '0004_contact_alter_faq_options_alter_faqcategory_options'),
        ('quiz', '0002_alter_quizgroup_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', config.utils.CustomAutoField(editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('course', 'Course'), ('quiz', 'Quiz'), ('other', 'Other')], max_length=10)),
                ('message', models.TextField()),
                ('image', models.ImageField(null=True, upload_to='reports')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='course.course')),
                ('quiz', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='quiz.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'report',
                'verbose_name_plural': 'reports',
                'db_table': 'report',
                'ordering': ('id',),
            },
        ),
    ]
