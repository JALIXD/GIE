from django.urls import path
from . import views

urlpatterns = [
    path('fichaje/', views.panel_fichaje, name='panel_fichaje'),
    path('admin/horas/<int:user_id>/', views.ver_horas_de_usuario, name='ver_horas_usuario'),

]
