# Generated by Django 3.2.4 on 2022-03-29 04:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quantum', '0010_auto_20220324_1012'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='id_table',
            name='department_id',
        ),
    ]
