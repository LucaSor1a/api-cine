from django.db import models
from django.core.exceptions import ValidationError


def validate_state(estado):
    if estado != 'Activo' and estado != 'No activo':
            raise ValidationError(f'Estado has wrong value: {estado}. Estado should be Activo or Inactivo')


# Create your models here.
class Pelicula(models.Model):
    """ Modelo para las Peliculas en la base de datos """

    nombre = models.CharField(max_length=200)
    duracion = models.IntegerField()
    descripcion = models.CharField(max_length=350)
    genero = models.CharField(max_length=50)
    clasificacion = models.CharField(max_length=10)
    estado = models.CharField(max_length=25, validators=[validate_state])
    fecha_comienzo = models.DateField()
    fecha_finalizacion = models.DateField()


class Sala(models.Model):
    """ Modelo para las Salas en la base de datos """

    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=25)
    filas = models.IntegerField()
    asientos = models.IntegerField()


class Proyeccion(models.Model):
    """ Modelo para las Proyecciones en la base de datos """

    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    fecha_comienzo = models.DateField()
    fecha_finalizacion = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=25, validators=[validate_state])


class Reserva(models.Model):
    """ Modelo para las Reservas de butacas en la base de datos """

    proyeccion = models.ForeignKey(Proyeccion, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    fila = models.IntegerField()
    asiento = models.IntegerField()
