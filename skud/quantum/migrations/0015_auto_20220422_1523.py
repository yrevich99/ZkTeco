# Generated by Django 3.2.4 on 2022-04-22 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quantum', '0014_alter_grafik_grafik_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grafik',
            name='grafik_name',
            field=models.CharField(max_length=60, unique=True),
        ),
        migrations.AlterField(
            model_name='grafik',
            name='smena',
            field=models.CharField(max_length=60),
        ),
    ]
