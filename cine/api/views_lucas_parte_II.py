from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers_lucas_parte_I import ProyeccionSerializer, PeliculaSerializer, SalaSerializer, ReservaSerializer, ProyeccionHorarioSerializer
from .models import Pelicula, Proyeccion, Sala, Reserva
from rest_framework import status
from datetime import datetime
from django.db.models import Q
from .views_lucas_parte_I import comprobacion_fechas


class Proyecciones(APIView):
    """ Vista de todas las proyecciones de las peliculas activas + POST + PUT """

    def get(self, request):
        hoy = datetime.today()
        peliculas = Pelicula.objects.filter(estado='Activo')
        peliculas = PeliculaSerializer(peliculas, many=True)
        resultado = []
        for dic in peliculas.data:
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
        proyeccion = ProyeccionSerializer(data=request.data)
        if proyeccion.is_valid():
            if not comprobacion_fechas(proyeccion.validated_data['fecha_comienzo'].strftime('%Y-%m-%d') , proyeccion.validated_data['fecha_finalizacion'].strftime('%Y-%m-%d')):
                return Response({'state': 'failure', 'request': request.data, 'error': {'fecha_finalizacion': ['Fecha finalizacion has wrong value. Fecha finalizacion shoud be greater than Fecha comienzo']}}, status=status.HTTP_400_BAD_REQUEST)
            proyeccion.save()
            return Response({'state': 'successful', 'request': proyeccion.data})
        else:
            return Response({'state': 'failure', 'request': request.data, 'error': proyeccion.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            objeto = Proyeccion.objects.get(pk=request.data['id'])
        except (Proyeccion.DoesNotExist, KeyError):
            try:
                return Response({'error': 'NOT FOUND', 'request': {'id': request.data['id']}}, status=status.HTTP_404_NOT_FOUND)
            except KeyError:
                return Response({'error': 'NOT FOUND', 'request': {'id': 'None'}}, status=status.HTTP_404_NOT_FOUND)
        proyeccion = ProyeccionSerializer(objeto, data=request.data)
        if proyeccion.is_valid():
            proyeccion.save()
            return Response({'state': 'successful', 'request': proyeccion.data})
        else:
            return Response({'state': 'failure', 'request': request.data, 'error': proyeccion.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProyeccionesRango(APIView):
    """ Vista de todas las proyecciones de peliculas activas en un rango de fechas """

    def get(self, request, inicio, fin):
        if comprobacion_fechas(inicio, fin):
            peliculas = Pelicula.objects.filter(estado='Activo')
            peliculas = PeliculaSerializer(peliculas, many=True)
            resultado = []
            for dic in peliculas.data:
                pelicula_id = dic['id']
                pelicula_nombre = dic['nombre']
                proyecciones = Proyeccion.objects.filter(pelicula=pelicula_id, estado='Activo').exclude((Q(fecha_comienzo__gt=inicio) & Q(fecha_comienzo__gt=fin)) | (Q(fecha_finalizacion__lt=inicio) & Q(fecha_finalizacion__lt=fin)))
                json_proyecciones = ProyeccionHorarioSerializer(proyecciones, many=True)
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
            return Response({'error': 'BAD REQUEST', 'request': {'fecha_comienzo': inicio, 'fecha_finalizacion': fin}}, status=status.HTTP_400_BAD_REQUEST)


class ProyeccionFecha(APIView):
    """ Vista de todas las proyecciones de una pelicula + su informacion sobre la sala y butacas """

    def get(self, request, pk, fecha):
        if comprobacion_fechas(fecha):
            try:
                proyecciones = Proyeccion.objects.get(id=pk, fecha_comienzo__lte=fecha, fecha_finalizacion__gte=fecha)
            except Proyeccion.DoesNotExist:
                return Response({'error': 'NOT FOUND', 'request': {'id': pk, 'fecha': fecha}}, status=status.HTTP_404_NOT_FOUND)
            json_proyecciones = ProyeccionSerializer(proyecciones)
            dic = json_proyecciones.data
            pelicula = Pelicula.objects.get(pk=dic['pelicula'])
            json_pelicula = PeliculaSerializer(pelicula)
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
            resultado = {
                'pelicula': json_pelicula.data,
                'sala': json_sala.data,
                'butacas': butacas_posiciones,
            }
            return Response(resultado)
        else:
            return Response({'error': 'BAD REQUEST', 'request': {'fecha': fecha}}, status=status.HTTP_400_BAD_REQUEST)
