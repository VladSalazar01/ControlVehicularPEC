# Generated by Django 4.2.2 on 2023-07-22 05:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0012_remove_ordencombustible_ordende_trabajo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordencombustible',
            name='tecnico',
        ),
        migrations.RemoveField(
            model_name='ordenmantenimiento',
            name='tecnico',
        ),
        migrations.AddField(
            model_name='ordencombustible',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordenmantenimiento',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
