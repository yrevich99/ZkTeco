# Generated by Django 3.2.4 on 2022-04-16 05:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quantum', '0012_grafik'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grafik',
            name='smena',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='quantum.smena'),
        ),
    ]
