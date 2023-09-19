# Generated by Django 4.2.2 on 2023-09-18 15:44

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('home', '0033_ordencombustible_fecha_de_entrega_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProxy',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
