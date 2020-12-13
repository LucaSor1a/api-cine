from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers_lucas_parte_I import ProyeccionSerializer, PeliculaSerializer, SalaSerializer, ReservaSerializer, ProyeccionHorarioSerializer
from .models import Pelicula, Proyeccion, Sala, Reserva
from rest_framework import status
from datetime import datetime, timedelta, date
from django.db.models import Q
from .views_lucas_parte_I import comprobacion_fechas


class Proyecciones(APIView):
    """ Vista de todas las proyecciones de las peliculas activas hoy + POST + PUT """

    def superposicion_proyeccion(self, pelicula, sala, fecha, hora, id=None):
        """ Comprueba que no haya superposicion de proyecciones en una misma sala """

        proyecciones = Proyeccion.objects.filter(sala=sala).filter(estado__in=('A', 'Activo')).filter(Q(fecha_comienzo__lte=fecha) & Q(fecha_finalizacion__gte=fecha))
        json_proyecciones = ProyeccionSerializer(proyecciones, many=True)
        pelicula = PeliculaSerializer(pelicula)
        duracion = pelicula.data['duracion']
        for dic in json_proyecciones.data:
            pelicula = Pelicula.objects.get(pk=dic['pelicula'])
            json_pelicula = PeliculaSerializer(pelicula)
            inicio_nueva = hora
            inicio_vieja = datetime.strptime(dic['hora'], '%H:%M:%S').time()
            fin_nueva = (datetime.combine(date(1, 1, 1), hora) + timedelta(minutes=duracion + 30)).time()
            fin_vieja = (datetime.strptime(dic['hora'], '%H:%M:%S') + timedelta(minutes=json_pelicula.data['duracion'] + 30)).time()
            doce = datetime.strptime('12:00:00', '%H:%M:%S').time()
            if dic['id'] != id:
                if not (fin_nueva <= inicio_vieja or inicio_nueva >= fin_vieja):
                    return True
                elif (inicio_vieja > doce and fin_vieja < doce) and (inicio_nueva > doce and fin_nueva < doce):
                    return True
        return False
    

    def rango_correcto(self, proyeccion, pelicula):
        if proyeccion['fecha_comienzo'] >= datetime.strptime(pelicula['fecha_comienzo'], '%Y-%m-%d').date() and proyeccion['fecha_finalizacion'] <= datetime.strptime(pelicula['fecha_finalizacion'], '%Y-%m-%d').date():
            return True
        else:
            return False


    def get(self, request):
        hoy = datetime.today()
        peliculas = Pelicula.objects.filter(estado__in=('A', 'Activo'))
        peliculas = PeliculaSerializer(peliculas, many=True)
        resultado = []
        for dic in peliculas.data:
            pelicula_id = dic['id']
            pelicula_nombre = dic['nombre']
            proyecciones = Proyeccion.objects.filter(pelicula=pelicula_id, estado__in=('A', 'Activo')).filter(Q(fecha_comienzo__lte=hoy) & Q(fecha_finalizacion__gte=hoy))
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

    def post(self, request):
        proyeccion = ProyeccionSerializer(data=request.data)
        if proyeccion.is_valid():
            if not comprobacion_fechas(proyeccion.validated_data['fecha_comienzo'].strftime('%Y-%m-%d') , proyeccion.validated_data['fecha_finalizacion'].strftime('%Y-%m-%d')):
                return Response({'state': 'failure', 'request': request.data, 'error': {'fecha_finalizacion': ['Fecha finalizacion has wrong value. Fecha finalizacion shoud be greater than Fecha comienzo']}}, status=status.HTTP_400_BAD_REQUEST)
            if self.superposicion_proyeccion(proyeccion.validated_data['pelicula'], proyeccion.validated_data['sala'], proyeccion.validated_data['fecha_comienzo'], proyeccion.validated_data['hora']):
                return Response({'state': 'failure', 'request': request.data, 'error': {'proyeccion': ['Sala already occupied']}}, status=status.HTTP_400_BAD_REQUEST)
            pelicula = PeliculaSerializer(proyeccion.validated_data['pelicula'])
            if not self.rango_correcto(proyeccion.validated_data, pelicula.data):
                return Response({'state': 'failure', 'request': request.data, 'error': {'objeto': ['proyeccion', 'pelicula'], 'fecha_comienzo': [proyeccion.validated_data['fecha_comienzo'], pelicula.data['fecha_comienzo']], 'fecha_finalizacion': [proyeccion.validated_data['fecha_finalizacion'], pelicula.data['fecha_finalizacion']]}}, status=status.HTTP_400_BAD_REQUEST)
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
        id = int(proyeccion.initial_data['id'])
        if proyeccion.is_valid():
            if not comprobacion_fechas(proyeccion.validated_data['fecha_comienzo'].strftime('%Y-%m-%d') , proyeccion.validated_data['fecha_finalizacion'].strftime('%Y-%m-%d')):
                return Response({'state': 'failure', 'request': request.data, 'error': {'fecha_finalizacion': ['Fecha finalizacion has wrong value. Fecha finalizacion shoud be greater than Fecha comienzo']}}, status=status.HTTP_400_BAD_REQUEST)
            if self.superposicion_proyeccion(proyeccion.validated_data['pelicula'], proyeccion.validated_data['sala'], proyeccion.validated_data['fecha_comienzo'], proyeccion.validated_data['hora'], id):
                return Response({'state': 'failure', 'request': request.data, 'error': {'proyeccion': ['Sala already occupied']}}, status=status.HTTP_400_BAD_REQUEST)
            pelicula = PeliculaSerializer(proyeccion.validated_data['pelicula'])
            if not self.rango_correcto(proyeccion.validated_data, pelicula.data):
                return Response({'state': 'failure', 'request': request.data, 'error': {'objeto': ['proyeccion', 'pelicula'], 'fecha_comienzo': [proyeccion.validated_data['fecha_comienzo'], pelicula.data['fecha_comienzo']], 'fecha_finalizacion': [proyeccion.validated_data['fecha_finalizacion'], pelicula.data['fecha_finalizacion']]}}, status=status.HTTP_400_BAD_REQUEST)
            proyeccion.save()
            return Response({'state': 'successful', 'request': proyeccion.data})
        else:
            return Response({'state': 'failure', 'request': request.data, 'error': proyeccion.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProyeccionesRango(APIView):
    """ Vista de todas las proyecciones de peliculas activas en un rango de fechas """

    def get(self, request, inicio, fin):
        if comprobacion_fechas(inicio, fin):
            peliculas = Pelicula.objects.filter(estado__in=('A', 'Activo'))
            peliculas = PeliculaSerializer(peliculas, many=True)
            resultado = []
            for dic in peliculas.data:
                pelicula_id = dic['id']
                pelicula_nombre = dic['nombre']
                proyecciones = Proyeccion.objects.filter(pelicula=pelicula_id, estado__in=('A', 'Activo')).exclude((Q(fecha_comienzo__gt=inicio) & Q(fecha_comienzo__gt=fin)) | (Q(fecha_finalizacion__lt=inicio) & Q(fecha_finalizacion__lt=fin)))
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
