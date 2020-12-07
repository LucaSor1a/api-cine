from rest_framework import serializers
from .models import Sala, Pelicula, Proyeccion, Reserva


class PeliculaSerializer(serializers.ModelSerializer):
    """ Serializador relacionado al modelo de Peliculas """

    class Meta:
        model = Pelicula
        fields = ['id', 'nombre', 'duracion', 'descripcion', 'genero', 'clasificacion', 'estado', 'fecha_comienzo', 'fecha_finalizacion']


class SalaSerializer(serializers.ModelSerializer):
    """ Serializador relacionado al modelo de Salas """

    class Meta:
        model = Sala
        fields = ['id', 'nombre', 'estado', 'filas', 'asientos']


class ProyeccionSerializer(serializers.ModelSerializer):
    """ Serializador relacionado al modelo de Proyecciones """

    class Meta:
        model = Proyeccion
        fields = ['id', 'sala', 'pelicula', 'fecha_comienzo', 'fecha_finalizacion', 'hora', 'estado']


    def create(self, validated_data):
        return Proyeccion.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.sala = validated_data.get('sala', instance.sala)
        instance.pelicula = validated_data.get('pelicula', instance.pelicula)
        instance.fecha_comienzo = validated_data.get('fecha_comienzo', instance.fecha_comienzo)
        instance.fecha_finalizacion = validated_data.get('fecha_finalizacion', instance.fecha_finalizacion)
        instance.hora = validated_data.get('hora', instance.hora)
        instance.estado = validated_data.get('estado', instance.estado)
        instance.save()
        return instance


class ReservaSerializer(serializers.ModelSerializer):
    """ Serializador relacionado al modelo de Reservas de butacas """

    class Meta:
        model = Reserva
        fields = ['id', 'proyeccion', 'fecha', 'fila', 'asiento']


class ProyeccionHorarioSerializer(serializers.ModelSerializer):
    """ Serializador relacionado al modelo de Proyecciones que obtiene solo datos de tiempo """

    class Meta:
        model = Proyeccion
        fields = ['id', 'sala', 'fecha_comienzo', 'fecha_finalizacion', 'hora']
