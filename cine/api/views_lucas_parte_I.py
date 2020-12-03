from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_GET
from .serializers_lucas_parte_I import ProyeccionSerializer, PeliculaSerializer
from datetime import datetime
from .models import Pelicula, Proyeccion
from django.db.models import Q
import re


def comprobacion_fechas(inicio, fin):
    fecha = r'\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3(0|1))'
    if re.match(fecha, inicio) and re.match(fecha, fin):
        inicio = datetime.strptime(inicio, '%Y-%m-%d')
        fin = datetime.strptime(fin, '%Y-%m-%d')
        if inicio < fin:
            return True
        else:
            return False
    else:
        return False


class Peliculas():

    @require_GET
    def todas(self):
        pass

    @require_GET
    def todas_rango(self, inicio, fin):
        if comprobacion_fechas(inicio, fin):
            try:
                peliculas = Pelicula.objects.filter(Q(fecha_comienzo__range=[inicio, fin]) | Q(fecha_finalizacion__range=[inicio, fin]))
                json = PeliculaSerializer(peliculas, many=True)
                return JsonResponse(json.data, safe=False)
            except Pelicula.DoesNotExist:
                return HttpResponse(status=404)
        else:
            return HttpResponseBadRequest("Fechas incorrectas")

    @require_GET
    def una_rango(self, pk, inicio, fin):
        if comprobacion_fechas(inicio, fin):
            try:
                pelicula = Pelicula.objects.get(pk=pk)
                proyecciones = Proyeccion.objects.filter(pelicula=pk, estado='Activo')
                json_pelicula = PeliculaSerializer(pelicula)
                json_proyecciones = ProyeccionSerializer(proyecciones, many=True)
                return JsonResponse((json_pelicula.data, json_proyecciones.data), safe=False)
            except (Pelicula.DoesNotExist, Proyeccion.DoesNotExist):
                return HttpResponse(status=404)
        else:
            return HttpResponseBadRequest("Fechas incorrectas")
