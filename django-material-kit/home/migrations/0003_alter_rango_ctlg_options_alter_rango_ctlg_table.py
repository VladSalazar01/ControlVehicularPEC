# Generated by Django 4.2.2 on 2023-07-11 05:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_parroquia_options_alter_provincia_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rango_ctlg',
            options={'verbose_name_plural': 'Rangos'},
        ),
        migrations.AlterModelTable(
            name='rango_ctlg',
            table='Rango',
        ),
    ]
