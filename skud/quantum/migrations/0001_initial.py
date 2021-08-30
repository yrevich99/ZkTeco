# Generated by Django 3.2.4 on 2021-08-26 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Devices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_name', models.CharField(max_length=250, unique=True)),
                ('device_ip', models.CharField(max_length=15, unique=True)),
                ('device_mac', models.CharField(max_length=150, unique=True)),
                ('serial_number', models.CharField(max_length=250)),
                ('device_type', models.CharField(max_length=20)),
                ('device_add', models.CharField(max_length=5)),
                ('main_door', models.CharField(max_length=15)),
                ('device_port', models.CharField(max_length=10)),
            ],
        ),
    ]