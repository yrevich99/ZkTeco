# Generated by Django 3.2.4 on 2022-01-10 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quantum', '0008_id_table_status_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='door_setting',
            name='device_id',
            field=models.CharField(default=2, max_length=250),
            preserve_default=False,
        ),
    ]
