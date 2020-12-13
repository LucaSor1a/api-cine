from django.db import models


# Create your models here.
class Pelicula(models.Model):
    nombre = models.CharField(max_length=200)
    duracion = models.IntegerField()
    descripcion = models.CharField(max_length=350)
    genero = models.CharField(max_length=50)
    clasificacion = models.CharField(max_length=10)
    estado = models.CharField(max_length=25)
    fecha_comienzo = models.DateField()
    fecha_finalizacion = models.DateField()


class Sala(models.Model):

    estados = [
        ("H", "habilitada"),
        ("D", "deshabilitada"),
        ("E", "eliminada")
        ]

    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=25, choices=estados)
    filas = models.IntegerField()
    asientos = models.IntegerField()


class Proyeccion(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    fecha_comienzo = models.DateField()
    fecha_finalizacion = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=25)


class Reserva(models.Model):
    proyeccion = models.ForeignKey(Proyeccion, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    fila = models.IntegerField()
    asiento = models.IntegerField()
