# Generated by Django 4.2.2 on 2023-09-22 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0039_alter_ocupante_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ordenmovilizacion',
            options={'verbose_name': 'Orden de movilización', 'verbose_name_plural': 'Ordenes de movilización'},
        ),
        migrations.AlterField(
            model_name='ordenmovilizacion',
            name='numero_ocupantes',
            field=models.IntegerField(default=0),
        ),
    ]
