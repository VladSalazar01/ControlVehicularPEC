# Generated by Django 4.2.2 on 2023-09-06 15:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0028_ordenmantenimiento_archivo_asociado'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordenmantenimiento',
            old_name='archivo_asociado',
            new_name='parte_asociado',
        ),
    ]
