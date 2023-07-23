# Generated by Django 4.2.2 on 2023-07-23 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_alter_partepolicial_tipo_parte'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partepolicial',
            name='orden_combustible',
        ),
        migrations.RemoveField(
            model_name='partepolicial',
            name='orden_mantenimiento',
        ),
        migrations.AddField(
            model_name='partepolicial',
            name='fecha_solicitud',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='partepolicial',
            name='kilometraje_actual',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
