from django.urls import path
from .views_lucas_parte_I import Peliculas


urlpatterns = [
    path('peliculas/', Peliculas.todas, name='peliculas'),
    path('peliculas/<str:inicio>/<str:fin>/', Peliculas.todas_rango, name='peliculas por fecha'),
    path('peliculas/<int:pk>/<str:inicio>/<str:fin>/', Peliculas.una_rango, name='pelicula por fecha'),
]
