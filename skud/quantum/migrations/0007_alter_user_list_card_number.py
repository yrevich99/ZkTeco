# Generated by Django 3.2.4 on 2022-01-08 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quantum', '0006_auto_20220107_0840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_list',
            name='card_number',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
