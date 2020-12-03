from rest_framework import serializers
from .models import Sala, Pelicula, Proyeccion, Reserva


class PeliculaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pelicula
        fields = ['id', 'nombre', 'duracion', 'descripcion', 'genero', 'clasificacion', 'estado', 'fecha_comienzo', 'fecha_finalizacion']


class SalaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sala
        fields = ['id', 'nombre', 'estado', 'filas', 'asientos']


class ProyeccionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proyeccion
        fields = ['id', 'sala', 'pelicula', 'fecha_comienzo', 'fecha_finalizacion', 'hora', 'estado']


class ReservaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reserva
        fields = ['id', 'proyeccion', 'fecha', 'fila', 'asiento']
