from django.urls import path
from .views_philipp_parte_I import SalaView, ButacaView


urlpatterns = [
    path('salas/', SalaView.as_view(), name='salas'),
    path('butacas/', ButacaView.as_view(), name='butacas'),
]
