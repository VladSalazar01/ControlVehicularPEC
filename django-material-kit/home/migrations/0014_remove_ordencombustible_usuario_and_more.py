# Generated by Django 4.2.2 on 2023-07-22 05:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0013_remove_ordencombustible_tecnico_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordencombustible',
            name='usuario',
        ),
        migrations.RemoveField(
            model_name='ordenmantenimiento',
            name='usuario',
        ),
        migrations.AddField(
            model_name='ordencombustible',
            name='aprobador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ordenes_combustible_aprobadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordencombustible',
            name='creador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ordenes_combustible_creadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordenmantenimiento',
            name='aprobador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ordenes_mantenimiento_aprobadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordenmantenimiento',
            name='creador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ordenes_mantenimiento_creadas', to=settings.AUTH_USER_MODEL),
        ),
    ]