from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
import re
from .serializers_lucas_parte_I import ProyeccionSerializer, PeliculaSerializer
from .models import Pelicula, Proyeccion
from django.db.models import Q


def comprobacion_fechas(inicio, fin=None):
    fecha = r'\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3(0|1))'
    if fin != None:
        if re.match(fecha, inicio) and re.match(fecha, fin):
            inicio = datetime.strptime(inicio, '%Y-%m-%d')
            fin = datetime.strptime(fin, '%Y-%m-%d')
            if inicio < fin:
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

    def get(self, request):
        pelicula = Pelicula.objects.filter(estado='Activo')
        json_pelicula = PeliculaSerializer(pelicula, many=True)
        return Response(json_pelicula.data)


class PeliculasRango(APIView):

    def get(self, request, inicio, fin):
        if comprobacion_fechas(inicio, fin):
            peliculas = Pelicula.objects.filter(Q(fecha_comienzo__range=[inicio, fin]) | Q(fecha_finalizacion__range=[inicio, fin]))
            json = PeliculaSerializer(peliculas, many=True)
            return Response(json.data)
        else:
            return Response({'request': 'BAD REQUEST'}, status=status.HTTP_400_BAD_REQUEST)


class PeliculaRango(APIView):

    def get(self, request, pk, inicio, fin):
        if comprobacion_fechas(inicio, fin):
            try:
                pelicula = Pelicula.objects.get(pk=pk)
                proyecciones = Proyeccion.objects.filter(pelicula=pk, estado='Activo')
                json_pelicula = PeliculaSerializer(pelicula)
                json_proyecciones = ProyeccionSerializer(proyecciones, many=True)
                respuesta = {
                    'info_pelicula': json_pelicula.data,
                    'proyecciones': json_proyecciones.data
                }
                return Response(respuesta)
            except Pelicula.DoesNotExist:
                return Response({'request': 'NOT FOUND'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'request': 'BAD REQUEST'}, status=status.HTTP_400_BAD_REQUEST)
