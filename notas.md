# Notas sobre comandos y acciones a realizar. Notas de la "investigacion"


## Crear proyecto de Django:
django-admin startproject myProyect

## Correr el server
python3 manage.py runserver
    * Se puede especificar el puerto con:
        - python3 manage.py runserver 0:8000
        - python3 manage.py runserver 0:4001
        - python3 manage.py runserver localhost:8000

## Crear una app
python3 manage.py startapp appName

## Views
Configurandola podemos hacer el index(request) y mostramos lo que se ve cuando entramos a una pagina. Cada clase define una pagina nueva.
El urls se puede configurar un url para cada una de esas paginas

from django.http import HttpResponse
import datetime

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def my_view(request):
    # ...
    if foo:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    else:
        return HttpResponse('<h1>Page was found</h1>')
    else:
        return HttpResponse(status=201)

def detail(request, poll_id):
    try:
        p = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        raise Http404("Poll does not exist")
    return render(request, 'polls/detail.html', {'poll': p})

Tambien se pueden modificar los handlers
    - handler400
    - handler403
    - handler404
    - handler500

Interesantemente se pueden crear views Async, pero para sacarle jugo realmente tenemos que usar un server asincrono


### Decorators
Los decoradores @require_http_methods(["GET", "POST"]) sirven para describir sobre las funciones a que verbo http sirven. Util para cuando se puede usar mas de uno. Si hay un solo metodo entonces: requiere_GET()




## URLs
Configura que urls puede manejar la app.

urlpatterns = [
    path('articles/2003/', views.special_case_2003),
    path('articles/<int:year>/', views.year_archive),
    path('articles/<int:year>/<int:month>/', views.month_archive),
    path('articles/<int:year>/<int:month>/<slug:slug>/', views.article_detail),
    path('articles/2003/', views.special_case_2003),
    re_path(r'^articles/(?P<year>[0-9]{4})/$', views.year_archive),
    re_path(r'^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.month_archive),
    path('<username>/blog/', include('foo.urls.blog')),
]
views.month_archive(request, year=2005, month=3)


Si se utliza include quedan mas prolijos para poder manejar cada link desde cada app             !Ver como usar eso


## Models

cada clase es una tabla

Una caracteristica interesante son las opciones, como:
class Person(models.Model):
    SHIRT_SIZES = (
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
    )
    name = models.CharField(max_length=60)
    shirt_size = models.CharField(max_length=1, choices=SHIRT_SIZES)


* ademas se les pude agregar valores por defecto, primary_key=True https://docs.djangoproject.com/en/3.1/ref/models/fields/#model-field-types 
* Hay que decirle a conf en installed apps que use la app que tiene los modelos, solo poniendo el nombre
* Los nombres de campo verbosos permiten agragar una descripcion

* En cuanto a las relaciones tenemos:
### Many to One:
ForeignKey requires a positional argument: the class to which the model is related.
usar django.db.models.ForeignKey. 

from django.db import models

class Manufacturer(models.Model):
    # ...
    pass

class Car(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    # ...


### Many to many
from django.db import models

class Topping(models.Model):
    # ...
    pass

class Pizza(models.Model):
    # ...
    toppings = models.ManyToManyField(Topping)

* https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.ManyToManyField.through es para cuando la relacion muchos a muchos tiene atributos que interesen


### One to one
from django.conf import settings
from django.db import models

class MySpecialUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    supervisor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supervisor_of',
    )


### Some interesting models facts
Se puede definir __str__() para dar la representacion de la clase


Se pueden usar y relacionar modelos entre apps

from django.db import models
from geography.models import ZipCode

class Restaurant(models.Model):
    # ...
    zip_code = models.ForeignKey(
        ZipCode,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

Si se quieren hacer modelos abstractos:
from django.db import models

class CommonInfo(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()

    class Meta:
        abstract = True

class Student(CommonInfo):
    home_group = models.CharField(max_length=5)


### Creating and saving
from blog.models import Blog
b = Blog(name='Beatles Blog', tagline='All the latest Beatles news.')
b.save()


john = Author.objects.create(name="John")
paul = Author.objects.create(name="Paul")
george = Author.objects.create(name="George")
ringo = Author.objects.create(name="Ringo")
entry.authors.add(john, paul, george, ringo)


Entry.objects.all().filter(pub_date__year=2006)
Entry.objects.filter(pub_date__lte='2006-01-01')

from datetime import timedelta
Entry.objects.filter(mod_date__gt=F('pub_date') + timedelta(days=3))


Blog.objects.get(pk=14)


Entry.objects.filter(pub_date__year=2005).delete()
b = Blog.objects.get(pk=1)
b.delete()
Entry.objects.all().delete()


Tambien se puede usar raw SQL



### Ejemplos
https://docs.djangoproject.com/en/3.1/topics/db/examples/one_to_one/
https://docs.djangoproject.com/en/3.1/topics/db/examples/many_to_one/
https://docs.djangoproject.com/en/3.1/topics/db/examples/many_to_many/



## Something

request.headers.get('user-agent')
request.build_absolute_uri('/bands/')


## Serializing
from django.core.serializers import serialize

serialize('json', SomeModel.objects.all(), cls=LazyEncoder)


## Deserializing
