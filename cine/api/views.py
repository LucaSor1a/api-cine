from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Pelicula, Proyeccion, Sala, Reserva
from .serializers import ProyeccionSerializer, PeliculaSerializer, SalaSerializer, ReservaSerializer, ProyeccionHorarioSerializer
from datetime import datetime, timedelta, date
import re


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
        pelicula = Pelicula.objects.filter(estado__in=('A', 'Activo'))
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
                proyecciones = Proyeccion.objects.filter(pelicula=pk, estado__in=('A', 'Activo')).exclude((Q(fecha_comienzo__gt=inicio) & Q(fecha_comienzo__gt=fin)) | (Q(fecha_finalizacion__lt=inicio) & Q(fecha_finalizacion__lt=fin)))
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


class SalaView(APIView):
    """ Vista de todas las salas o de una sala especifica + POST + PUT + DELETE """

    # cambiar data request

    def get(self, request, pk=None):

        if pk:
            sala = Sala.objects.filter(pk=pk)
        else:
            sala = Sala.objects.all()

        response = SalaSerializer(sala, many=True)
        return Response(response.data)

    def post(self, request):

        data = request.data

        serializer = SalaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data)
        return Response(serializer.errors, status=400)

    def put(self, request, pk=None):

        data = request.data
        if pk:
            pk = pk
        elif "pk" in data.keys():
            pk = data.pop("pk")
        else:
            return Response("pk required", status=400)

        sala = Sala.objects.get(pk=pk)
        serializer = SalaSerializer(sala, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def delete(self, request):

        if "pk" in request.data.keys():
            pk = request.data["pk"]
            try:
                sala = Sala.objects.get(pk=pk)
            except Sala.DoesNotExist:
                error_msg = "sala pk=" + str(pk) + " does not exist"
                return Response(error_msg, status=400)
        else:
            error_msg = str(request.data) + "   no private key provided"
            return Response(error_msg, status=400)

        if "force" in request.data.keys() and request.data["force"] is True:
            sala.delete()
            response = "sala pk=" + str(pk) + " eliminada"
        else:
            sala.estado = "eliminada"
            response = SalaSerializer(sala).data

        sala.save()
        return Response(response)


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
        """ Se fija que las fechas de la proyeccion esten dentro de las fechas de la pelicula """

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


class ButacaView(APIView):
    """ Lista de todas las butacas o una butaca especifica + POST + PUT """

    def get(self, request, pk=None):

        if pk:
            butaca = Reserva.objects.filter(pk=pk)
        else:
            butaca = Reserva.objects.all()

        response = ReservaSerializer(butaca, many=True)
        return Response(response.data)

    def post(self, request):

        data = request.data

        serializer = ReservaSerializer(data=data)

        if serializer.is_valid() and self.asiento_isvalid(data["proyeccion"],
                                                          data["fila"],
                                                          data["asiento"]):
            serializer.save()
            return Response(data)
        return Response(serializer.errors or self.asiento_errors, status=400)

    def put(self, request, pk=None):

        data = request.data
        if pk:
            pk = pk
        elif "pk" in data:
            pk = data.pop("pk")
        else:
            return Response("pk required", status=400)

        butaca = Reserva.objects.get(pk=pk)
        serializer = ReservaSerializer(butaca, data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        do_filas = self.asiento_isvalid(
                                    butaca.proyeccion,
                                    data.get("fila"),
                                    data.get("asiento")
                                    )

        do_date = self.fecha_valid(
                                    butaca.proyeccion,
                                    data.get("fecha")
                                    )

        is_not_repeated = self.validate_repetition(
                                    data.get("fecha"),
                                    data.get("fila"),
                                    data.get("asiento"),
                                    pk=pk
                                    )

        if do_filas and do_date and is_not_repeated:
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                {
                    **self.asiento_errors,
                    **self.fecha_errors,
                    **self.repetition_errors
                    },
                status=400
                )

    def asiento_isvalid(self, instance, fila=0, asiento=0):
        """ Validacion de los asientos existen en la sala """

        self.asiento_errors = {}

        if isinstance(instance, int):
            instance = Proyeccion.objects.get(pk=instance)

        if not (isinstance(fila, int) and isinstance(asiento, int)):
            return False

        fila_validity = fila <= instance.sala.filas and fila > 0
        asiento_validity = asiento <= instance.sala.asientos and asiento > 0

        if not fila_validity:
            self.asiento_errors["fila"] = [
                f"No se existe la fila {fila} en la sala {instance.sala.pk}"
            ]

        if not asiento_validity:
            self.asiento_errors["asiento"] = [
                f"No se existe el asiento {asiento} en la sala {instance.sala.pk}"
            ]

        return fila_validity and asiento_validity

    def fecha_valid(self, instancia, fecha):
        """ Validacion de que la butaca es vendida dentro del rango de fechas de la proyeccion """

        self.fecha_errors = {}

        fecha = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%SZ")

        if instancia.fecha_comienzo <= datetime.date(fecha) <= instancia.fecha_finalizacion:
            return True
        else:
            self.fecha_errors["fecha de proyeccion"] = [
                "la fecha de la reserva esta fuera de la fecha de la proyeccion"
            ]
            return False

    def validate_repetition(self, fecha, fila, asiento, pk=None):
        """ Validar de que no se venda la misma butaca el mismo dia """

        self.repetition_errors = {}
        existente = Reserva.objects.filter(fecha=fecha, fila=fila, asiento=asiento)
        ids = [i["id"] for i in existente.values()]

        if existente.count() == 0:
            return True
        elif pk in ids:
            return True
        else:
            self.repetition_errors["reserva existente"] = [
                "ya existe una reserva en ese dia para esa butaca"
            ]
            return False
