# Generated by Django 3.2.4 on 2022-02-05 17:49

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Access_control',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_name', models.CharField(max_length=250, unique=True)),
                ('lock_control', models.CharField(max_length=250)),
                ('time_zone', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Access_id',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_id', models.IntegerField(blank=True, null=True)),
                ('device_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
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
        migrations.CreateModel(
            name='Door_setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('door_number', models.IntegerField()),
                ('name_door', models.CharField(max_length=250, unique=True)),
                ('device_name', models.CharField(max_length=250)),
                ('device_ip', models.CharField(max_length=250)),
                ('driver_time', models.IntegerField()),
                ('detector_time', models.IntegerField()),
                ('inter_time', models.IntegerField()),
                ('sensor_type', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Id_table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('department_id', models.IntegerField(blank=True, null=True)),
                ('access_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Status_access',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=15)),
                ('user_card', models.CharField(max_length=50)),
                ('access_lock', models.CharField(max_length=15)),
                ('device_ip', models.CharField(max_length=30)),
                ('status_access', models.BooleanField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User_list',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('images', models.BinaryField(blank=True)),
                ('surname', models.CharField(max_length=150)),
                ('name', models.CharField(max_length=150)),
                ('department_id', models.IntegerField()),
                ('card_number', models.CharField(max_length=50, unique=True)),
                ('access_id', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='quantum.department')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
