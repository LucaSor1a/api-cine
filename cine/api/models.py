from django.db import models


ESTADOS = [
    ('A', 'Activo'),
    ('N', 'No activo')
]


# Create your models here.
class Pelicula(models.Model):
    """ Modelo para las Peliculas en la base de datos """

    nombre = models.CharField(max_length=200)
    duracion = models.IntegerField()
    descripcion = models.CharField(max_length=350)
    genero = models.CharField(max_length=50)
    clasificacion = models.CharField(max_length=10)
    estado = models.CharField(max_length=25, choices=ESTADOS, default='N')
    fecha_comienzo = models.DateField()
    fecha_finalizacion = models.DateField()


class Sala(models.Model):
    """ Modelo para las Salas en la base de datos """

    estados = [
        ('H', 'Habilitada'),
        ('D', 'Deshabilitada'),
        ('E', 'Eliminada')
        ]

    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=25, choices=estados, default='D')
    filas = models.IntegerField()
    asientos = models.IntegerField()


class Proyeccion(models.Model):
    """ Modelo para las Proyecciones en la base de datos """

    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    fecha_comienzo = models.DateField()
    fecha_finalizacion = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=25, choices=ESTADOS, default='N')


class Reserva(models.Model):
    """ Modelo para las Reservas de butacas en la base de datos """

    proyeccion = models.ForeignKey(Proyeccion, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    fila = models.IntegerField()
    asiento = models.IntegerField()
