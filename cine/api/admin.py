from django.contrib import admin
from .models import Pelicula, Sala, Proyeccion, Reserva


# Register your models here.
# Esto permite ver y modificar en la pagina de admin los distintos modelos
admin.site.register(Pelicula)
admin.site.register(Sala)
admin.site.register(Proyeccion)
admin.site.register(Reserva)
