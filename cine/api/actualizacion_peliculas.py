import requests
from datetime import datetime
from .models import Pelicula


# substraccion de conjuntos para listas
def subtraction(list1, list2):
    result = []
    for i in list1:
        if i not in list2:
            result.append(i)
    return result


# actualizacion para una pelicula, si no existe, se crea
def update_movie_list(pelicula):
    Pelicula.objects.update_or_create(
        id=pelicula.get('id'),
        defaults={
            'nombre': pelicula.get('nombre'),
            'duracion': pelicula.get('duracion'),
            'descripcion': pelicula.get('descripcion'),
            'genero': pelicula.get('genero'),
            'clasificacion': pelicula.get('clasificacion'),
            'estado': pelicula.get('estado'),
            'fecha_comienzo': pelicula.get('fecha_comienzo'),
            'fecha_finalizacion': pelicula.get('fecha_finalizacion')
        })


# eliminar pelicula
def eliminar_pelicula(pelicula):
    pel = Pelicula.objects.get(pk=pelicula['id'])
    pel.delete()


def adapt(service_list):
    for i in service_list:
        del i['detalle']
        i['fecha_comienzo'] = datetime.date(datetime.strptime(i.pop('fechaComienzo'), '%Y-%m-%dT%H:%M:%S+%f'))
        i['fecha_finalizacion'] = datetime.date(datetime.strptime(i.pop('fechaFinalizacion'), '%Y-%m-%dT%H:%M:%S+%f'))
    return service_list


def do_update():

    # get al servicio y a la BD para ver las peliculas
    service_response = requests.get('http://localhost:8080/api/pelicula/')
    db_response = Pelicula.objects.all()

    # se lee la respuesta de los servidores como json
    service_list = adapt(service_response.json())
    db_list = list(db_response.values())

    # debug # print("\n\na", service_list,"\n\nb", db_list)

    # se busca la diferencia entre las peliculas del servicio y las de la BD
    to_add = subtraction(service_list, db_list)
    # debug # print("\n\nto_add", to_add)

    # map(update_movie_list, to_add)
    for i in to_add:
        update_movie_list(i)

    # se hace otro get request a la BD para tener el json actualizado
    # asi no se eliminan las peliculas que debian ser actualizadas
    db_response = Pelicula.objects.all()
    db_list = list(db_response.values())

    # se eliminan las peliculas que no estan en el servicio
    to_delete = subtraction(db_list, service_list)
    # debug # print("del", to_delete)

    # map(eliminar_pelicula, to_delete)
    for i in to_delete:
        eliminar_pelicula(i)
