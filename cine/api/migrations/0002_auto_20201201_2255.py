# Generated by Django 3.1 on 2020-12-01 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyeccion',
            name='hora',
            field=models.TimeField(),
        ),
    ]
