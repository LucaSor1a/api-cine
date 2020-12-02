from django.urls import path, re_path
from .views_lucas_parte_I import Peliculas


urlpatterns = [
    path('peliculas/', Peliculas.todas, name='peliculas'),
    re_path(r'peliculas/(?P<inicio>\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3(0|1)))/(?P<fin>\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3(0|1)))/$', Peliculas.todas_rango, name='peliculas por fecha'),
]
