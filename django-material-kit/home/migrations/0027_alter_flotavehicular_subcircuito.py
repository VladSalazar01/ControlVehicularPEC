# Generated by Django 4.2.2 on 2023-08-08 19:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_personalpolicial_subcircuito'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flotavehicular',
            name='subcircuito',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='flota_vehicular', to='home.subcircuitos'),
        ),
    ]
