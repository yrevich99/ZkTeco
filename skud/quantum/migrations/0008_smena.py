# Generated by Django 3.2.4 on 2022-03-11 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quantum', '0007_auto_20220303_1252'),
    ]

    operations = [
        migrations.CreateModel(
            name='Smena',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('smena_name', models.CharField(max_length=60)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('start_break', models.TimeField()),
                ('end_break', models.TimeField()),
            ],
        ),
    ]
