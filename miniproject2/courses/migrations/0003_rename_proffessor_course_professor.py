# Generated by Django 5.1.3 on 2024-11-18 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_rename_instructor_course_proffessor'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='proffessor',
            new_name='professor',
        ),
    ]
