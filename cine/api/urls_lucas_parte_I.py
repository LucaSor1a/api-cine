from django.urls import path
from .views_lucas_parte_I import Peliculas, PeliculasRango, PeliculaRango
from .views_lucas_parte_II import Proyecciones, ProyeccionesRango, ProyeccionFecha


urlpatterns = [
    # Endpoint de consulta de peliculas
    path('peliculas/', Peliculas.as_view(), name='Peliculas'),
    path('peliculas/<str:inicio>/<str:fin>/', PeliculasRango.as_view(), name='Peliculas por fecha'),
    path('peliculas/<int:pk>/<str:inicio>/<str:fin>/', PeliculaRango.as_view(), name='Pelicula por fecha'),

    # Endpoint de consultas de proyeccion
    path('proyecciones/', Proyecciones.as_view(), name='Proyecciones'),
    path('proyecciones/<int:pk>/<str:fecha>/', ProyeccionFecha.as_view(), name='Proyeccion en una fecha'),
    path('proyecciones/<str:inicio>/<str:fin>/', ProyeccionesRango.as_view(), name='Proyecciones por fecha'),
]
