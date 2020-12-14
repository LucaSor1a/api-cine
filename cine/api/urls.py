from django.urls import path
from .views import Peliculas, PeliculasRango, PeliculaRango, Proyecciones, ProyeccionesRango, ProyeccionFecha, SalaView, ButacaView


urlpatterns = [
    # Endpoint de consulta de peliculas
    path('peliculas/', Peliculas.as_view(), name='Peliculas'),
    path('peliculas/<str:inicio>/<str:fin>/', PeliculasRango.as_view(), name='Peliculas por fecha'),
    path('peliculas/<int:pk>/<str:inicio>/<str:fin>/', PeliculaRango.as_view(), name='Pelicula por fecha'),

    # Endpoint de consulta de salas
    path('salas/', SalaView.as_view(), name='Salas'),
    path('salas/<int:pk>/', SalaView.as_view(), name='Salas'),

    # Endpoint de consultas de proyeccion
    path('proyecciones/', Proyecciones.as_view(), name='Proyecciones'),
    path('proyecciones/<int:pk>/<str:fecha>/', ProyeccionFecha.as_view(), name='Proyeccion en una fecha'),
    path('proyecciones/<str:inicio>/<str:fin>/', ProyeccionesRango.as_view(), name='Proyecciones por fecha'),

    # Endpoint de consulta de butacas
    path('butacas/', ButacaView.as_view(), name='Butacas'),
    path('butacas/<int:pk>/', ButacaView.as_view(), name='Butacas'),
]
