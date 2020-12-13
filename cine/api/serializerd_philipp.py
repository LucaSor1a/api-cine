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

    def update(self, instance, validated_data):

        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.estado = validated_data.get('estado', instance.estado)
        instance.filas = validated_data.get('filas', instance.filas)
        instance.asientos = validated_data.get('asientos', instance.asientos)
        instance.save()
        return instance


class ProyeccionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proyeccion
        fields = ['id', 'sala', 'pelicula', 'fecha_comienzo', 'fecha_finalizacion', 'hora', 'estado']


class ReservaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reserva
        fields = ['id', 'proyeccion', 'fecha', 'fila', 'asiento']

    def update(self, instance, validated_data):

        instance.proyeccion = validated_data.get('proyeccion', instance.proyeccion)
        instance.fecha = validated_data.get('fecha', instance.fecha)
        instance.fila = validated_data.get('fila', instance.fila)
        instance.asiento = validated_data.get('asiento', instance.asiento)
        instance.save()
        return instance
