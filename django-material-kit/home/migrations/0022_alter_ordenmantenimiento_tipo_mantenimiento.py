# Generated by Django 4.2.2 on 2023-07-24 20:00

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0021_ordenmantenimiento_detalles_mantenimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordenmantenimiento',
            name='tipo_mantenimiento',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('M1', 'Mantenimiento tipo 01'), ('M2', 'Mantenimiento tipo 02'), ('M3', 'Mantenimiento tipo 03')], max_length=2), blank=True, null=True, size=None),
        ),
    ]