# Generated by Django 3.2.4 on 2022-06-21 05:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quantum', '0019_alter_user_list_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_list',
            name='grafik',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quantum.grafik'),
        ),
    ]
