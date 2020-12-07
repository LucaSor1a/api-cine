from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
import re
from .serializers_lucas_parte_I import ProyeccionSerializer, PeliculaSerializer, ProyeccionHorarioSerializer
from .models import Pelicula, Proyeccion
from django.db.models import Q


def comprobacion_fechas(inicio, fin=None):
    """ Comprueba que las fechas ingresadas son validas """

    fecha = r'\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3(0|1))'
    if fin != None:
        if re.match(fecha, inicio) and re.match(fecha, fin):
            inicio = datetime.strptime(inicio, '%Y-%m-%d')
            fin = datetime.strptime(fin, '%Y-%m-%d')
            if inicio <= fin:
                return True
            else:
                return False
        else:
            return False
    else:
        if re.match(fecha, inicio):
            return True
        else:
            return False


class Peliculas(APIView):
    """ Vista de todas las peliculas Activas """

    def get(self, request):
        pelicula = Pelicula.objects.filter(estado='Activo')
        json_pelicula = PeliculaSerializer(pelicula, many=True)
        return Response(json_pelicula.data)


class PeliculasRango(APIView):
    """ Vista de las peliculas presentes en la base de datos con fechas dentro del rango """

    def get(self, request, inicio, fin):
        if comprobacion_fechas(inicio, fin):
            peliculas = Pelicula.objects.exclude((Q(fecha_comienzo__gt=inicio) & Q(fecha_comienzo__gt=fin)) | (Q(fecha_finalizacion__lt=inicio) & Q(fecha_finalizacion__lt=fin)))
            json = PeliculaSerializer(peliculas, many=True)
            return Response(json.data)
        else:
            return Response({'error': 'BAD REQUEST', 'request': {'fecha_comienzo': inicio, 'fecha_finalizacion': fin}}, status=status.HTTP_400_BAD_REQUEST)


class PeliculaRango(APIView):
    """ Vista de las proyecciones activas de una pelicula dentro de un rango de fechas """

    def get(self, request, pk, inicio, fin):
        if comprobacion_fechas(inicio, fin):
            try:
                pelicula = Pelicula.objects.get(pk=pk)
                proyecciones = Proyeccion.objects.filter(pelicula=pk, estado='Activo').exclude((Q(fecha_comienzo__gt=inicio) & Q(fecha_comienzo__gt=fin)) | (Q(fecha_finalizacion__lt=inicio) & Q(fecha_finalizacion__lt=fin)))
                json_pelicula = PeliculaSerializer(pelicula)
                json_proyecciones = ProyeccionHorarioSerializer(proyecciones, many=True)
                respuesta = {
                    'info_pelicula': json_pelicula.data,
                    'proyecciones': json_proyecciones.data
                }
                return Response(respuesta)
            except Pelicula.DoesNotExist:
                return Response({'error': 'NOT FOUND', 'request': {'id': pk}}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'BAD REQUEST', 'request': {'fecha_comienzo': inicio, 'fecha_finalizacion': fin}}, status=status.HTTP_400_BAD_REQUEST)
