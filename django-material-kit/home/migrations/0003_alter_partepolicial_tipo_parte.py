# Generated by Django 4.2.2 on 2023-06-29 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_tallermecanico_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partepolicial',
            name='tipo_parte',
            field=models.CharField(blank=True, choices=[('Mantenimiento Preventivo', 'Mantenimiento preventivo'), ('Mantenimiento emergente', 'Mantenimiento emergente'), ('Novedades', 'Novedades')], db_column='Tipo de Parte', max_length=26, null=True),
        ),
    ]
