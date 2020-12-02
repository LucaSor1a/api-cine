from django.http import HttpResponse
from django.views.decorators.http import require_GET
from .serializers_lucas_parte_I import serializacion_de_objetos
from datetime import datetime
from .models import Pelicula


class Peliculas():

    @require_GET
    def todas(self):
        with open('./api/peliculas.html', 'r') as html:
            return HttpResponse(html.read())

    @require_GET
    def todas_rango(self, inicio, fin):

        def comprobacion(inicio, fin):
            inicio = datetime.strptime(inicio, '%Y-%m-%d')
            fin = datetime.strptime(fin, '%Y-%m-%d')
            if inicio < fin:
                return True
            else:
                return False

        if comprobacion(inicio, fin):
            objetos = Pelicula.objects.filter(fecha_comienzo__range=[inicio, fin])
            json = serializacion_de_objetos(objetos)
            return HttpResponse(json, content_type='application/json')
