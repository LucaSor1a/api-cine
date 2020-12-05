from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers_lucas_parte_I import ProyeccionSerializer, PeliculaSerializer, SalaSerializer, ReservaSerializer
from .models import Pelicula, Proyeccion, Sala, Reserva
from rest_framework import status
from datetime import datetime
from django.db.models import Q
from .views_lucas_parte_I import comprobacion_fechas


class Proyecciones(APIView):

    def get(self, request):
        hoy = datetime.today()
        peliculas = Pelicula.objects.filter(estado='Activo')
        dict_peliculas = PeliculaSerializer(peliculas, many=True)
        resultado = []
        for dic in dict_peliculas.data:
            pelicula_id = dic['id']
            pelicula_nombre = dic['nombre']
            proyecciones = Proyeccion.objects.filter(pelicula=pelicula_id).filter(Q(fecha_comienzo__lte=hoy) & Q(fecha_finalizacion__gte=hoy))
            json_proyecciones = ProyeccionSerializer(proyecciones, many=True)
            if json_proyecciones.data != []:
                resultado.append({
                    'pelicula': {
                        'id': pelicula_id,
                        'nombre': pelicula_nombre
                    },
                    'proyecciones': json_proyecciones.data
                })
        return Response(resultado)

    def post(self, request):
        return Response(request.data)

    def put(self, request):
        return Response(request.data)


class ProyeccionesRango(APIView):

    def get(self, request, inicio, fin):
        if comprobacion_fechas(inicio, fin):
            peliculas = Pelicula.objects.filter(estado='Activo')
            dict_peliculas = PeliculaSerializer(peliculas, many=True)
            resultado = []
            for dic in dict_peliculas.data:
                pelicula_id = dic['id']
                pelicula_nombre = dic['nombre']
                proyecciones = Proyeccion.objects.filter(pelicula=pelicula_id).filter(Q(fecha_comienzo__range=[inicio, fin]) | Q(fecha_finalizacion__range=[inicio, fin]))
                json_proyecciones = ProyeccionSerializer(proyecciones, many=True)
                if json_proyecciones.data != []:
                    resultado.append({
                        'pelicula': {
                            'id': pelicula_id,
                            'nombre': pelicula_nombre
                        },
                        'proyecciones': json_proyecciones.data
                    })
            return Response(resultado)
        else:
            return Response({'request': 'BAD REQUEST'}, status=status.HTTP_400_BAD_REQUEST)


class ProyeccionFecha(APIView):

    def get(self, request, pk, fecha):
        if comprobacion_fechas(fecha):
            proyecciones = Proyeccion.objects.filter(pelicula=pk).filter(Q(fecha_comienzo__lte=fecha) & Q(fecha_finalizacion__gte=fecha))
            json_proyecciones = ProyeccionSerializer(proyecciones, many=True)
            resultado = []
            for dic in json_proyecciones.data:
                sala = Sala.objects.get(pk=dic['sala'])
                json_sala = SalaSerializer(sala)
                butacas = Reserva.objects.filter(proyeccion=dic['id'])
                json_butacas = ReservaSerializer(butacas, many=True)
                butacas_posiciones = {}
                c = 0
                butacas = json_butacas.data
                for i in range(json_sala.data['filas']):
                    for j in range(json_sala.data['asientos']):
                        for butaca in butacas:
                            if butaca['fila'] - 1 == i and butaca['asiento'] - 1 == j:
                                butacas_posiciones[c] = {
                                        'fila': butaca['fila'],
                                        'asiento': butaca['asiento'],
                                        'estado': 'reservado',
                                }
                                butacas.remove(butaca)
                        try:
                            butacas_posiciones[c]
                        except:
                            butacas_posiciones[c] = {
                                'fila': i + 1,
                                'asiento': j + 1,
                                'estado': 'libre',
                            }
                        finally:
                            c += 1
                resultado.append({
                        'proyeccion': {
                            'id': dic['id'],
                            'fecha_comienzo': dic['fecha_comienzo'],
                            'fecha_finalizacion': dic['fecha_finalizacion'],
                            'hora': dic['hora'],
                            'sala': json_sala.data,
                            'butacas': butacas_posiciones,
                        }
                    })
            return Response(resultado)
        else:
            return Response({'request': 'BAD REQUEST'}, status=status.HTTP_400_BAD_REQUEST)
