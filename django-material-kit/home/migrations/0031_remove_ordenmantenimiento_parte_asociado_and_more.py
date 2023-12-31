# Generated by Django 4.2.2 on 2023-09-09 05:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0030_alter_ordenmantenimiento_parte_asociado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordenmantenimiento',
            name='parte_asociado',
        ),
        migrations.AddField(
            model_name='ordenmantenimiento',
            name='asunto',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ordenmantenimiento',
            name='detalle',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordenmantenimiento',
            name='parte_policial',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes_mantenimiento', to='home.partepolicial'),
        ),
    ]
