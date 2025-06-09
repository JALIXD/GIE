from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('nuevo/', views.crear_cliente, name='crear_cliente'),
    path('editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('clientes/<int:cliente_id>/compras/', views.compras_cliente, name='compras_cliente'),
    path('clientes/<int:cliente_id>/compras/pdf/', views.exportar_compras_pdf, name='exportar_compras_pdf'),
]
