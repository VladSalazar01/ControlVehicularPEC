# Generated by Django 4.2.2 on 2023-07-01 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_alter_partepolicial_tipo_parte'),
    ]

    operations = [
        migrations.AddField(
            model_name='partepolicial',
            name='estado',
            field=models.CharField(choices=[('En Proceso', 'En Proceso'), ('Completado', 'Completado'), ('Rechazado', 'Rechazado')], default='En Proceso', max_length=20),
        ),
    ]