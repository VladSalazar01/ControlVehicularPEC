# Generated by Django 4.2.2 on 2023-08-02 20:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0024_alter_ordencombustible_fecha_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordencombustible',
            name='aprobador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_aprobadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ordencombustible',
            name='creador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_creadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ordenmantenimiento',
            name='aprobador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_aprobadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ordenmantenimiento',
            name='creador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_creadas', to=settings.AUTH_USER_MODEL),
        ),
    ]