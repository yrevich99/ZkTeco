# Generated by Django 3.2.4 on 2022-01-10 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quantum', '0007_alter_user_list_card_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='id_table',
            name='status_access',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
