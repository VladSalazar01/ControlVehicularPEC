# Generated by Django 4.2.2 on 2023-07-23 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_remove_partepolicial_orden_combustible_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partepolicial',
            name='fecha',
            field=models.DateTimeField(blank=True, max_length=45, null=True),
        ),
    ]
