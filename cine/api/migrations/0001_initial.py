# Generated by Django 3.1 on 2020-12-01 19:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pelicula',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('duracion', models.IntegerField()),
                ('descripcion', models.CharField(max_length=350)),
                ('genero', models.CharField(max_length=50)),
                ('clasificacion', models.CharField(max_length=10)),
                ('estado', models.CharField(max_length=25)),
                ('fecha_comienzo', models.DateField()),
                ('fecha_finalizacion', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Proyeccion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_comienzo', models.DateField()),
                ('fecha_finalizacion', models.DateField()),
                ('hora', models.DateTimeField()),
                ('estado', models.CharField(max_length=25)),
                ('pelicula', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.pelicula')),
            ],
        ),
        migrations.CreateModel(
            name='Sala',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('estado', models.CharField(max_length=25)),
                ('filas', models.IntegerField()),
                ('asientos', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField()),
                ('fila', models.IntegerField()),
                ('asiento', models.IntegerField()),
                ('proyeccion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.proyeccion')),
            ],
        ),
        migrations.AddField(
            model_name='proyeccion',
            name='sala',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.sala'),
        ),
    ]
