# Generated by Django 4.2.2 on 2023-07-22 04:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_personalpolicial_is_deleted_tecnico_is_deleted_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordencombustible',
            name='ordende_trabajo',
        ),
        migrations.RemoveField(
            model_name='ordenmantenimiento',
            name='ordende_trabajo',
        ),
        migrations.AddField(
            model_name='ordencombustible',
            name='estado',
            field=models.CharField(blank=True, choices=[('Activa', 'Orden activa'), ('Despachada', 'Orden despachada')], db_column='Estado de Orden', max_length=26, null=True),
        ),
        migrations.AddField(
            model_name='ordencombustible',
            name='fecha',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='ordencombustible',
            name='tecnico',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='home.tecnico'),
        ),
        migrations.AddField(
            model_name='ordenmantenimiento',
            name='estado',
            field=models.CharField(blank=True, choices=[('Activa', 'Orden activa'), ('Despachada', 'Orden despachada')], db_column='Estado de Orden', max_length=26, null=True),
        ),
        migrations.AddField(
            model_name='ordenmantenimiento',
            name='fecha',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='ordenmantenimiento',
            name='tecnico',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='home.tecnico'),
        ),
        migrations.DeleteModel(
            name='OrdendeTrabajo',
        ),
    ]