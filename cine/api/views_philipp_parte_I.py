from .models import Sala, Reserva, Proyeccion
from .serializerd_philipp import SalaSerializer, ReservaSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime


class SalaView(APIView):

    # cambiar data request

    def get(self, request):

        if "pk" in request.data.keys():
            pk = request.data["pk"]
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

    def put(self, request):

        data = request.data
        pk = data.pop("pk")
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
            error_msg = str(request.data) + "<br>no private key provided"
            return Response(error_msg, status=400)

        if "force" in request.data.keys() and request.data["force"] is True:
            sala.delete()
            response = "sala pk=" + str(pk) + " eliminada"
        else:
            sala.estado = "eliminada"
            response = SalaSerializer(sala).data

        sala.save()
        return Response(response)


class ButacaView(APIView):

    def get(self, request):

        if "pk" in request.data.keys():
            pk = request.data["pk"]
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
        return Response(serializer.errors or self.asiento_errors, status=400)  # ver validacion en serializador

    def put(self, request):

        data = request.data
        if "pk" in data:
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
