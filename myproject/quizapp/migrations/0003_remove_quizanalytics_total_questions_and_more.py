# Generated by Django 4.2.3 on 2023-07-22 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizapp', '0002_alter_quizattempt_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quizanalytics',
            name='total_questions',
        ),
        migrations.RemoveField(
            model_name='quizattempt',
            name='score',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='email',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='username',
        ),
    ]
