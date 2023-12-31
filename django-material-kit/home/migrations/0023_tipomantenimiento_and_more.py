# Generated by Django 4.2.2 on 2023-07-25 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0022_alter_ordenmantenimiento_tipo_mantenimiento'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoMantenimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('M1', 'Mantenimiento tipo 01'), ('M2', 'Mantenimiento tipo 02'), ('M3', 'Mantenimiento tipo 03')], max_length=2)),
                ('descripcion', models.TextField(blank=True)),
                ('costo', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.RemoveField(
            model_name='ordenmantenimiento',
            name='detalles_mantenimiento',
        ),
        migrations.RemoveField(
            model_name='ordenmantenimiento',
            name='tipo_mantenimiento',
        ),
        migrations.AddField(
            model_name='ordenmantenimiento',
            name='tipos_mantenimiento',
            field=models.ManyToManyField(blank=True, to='home.tipomantenimiento'),
        ),
    ]
