from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    path('admin/ventas/', views.listar_ventas_admin, name='listar_ventas_admin'),
    path('admin/exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('admin/crear/tipo/', views.crear_tipo_venta, name='crear_tipo_venta'),
    path('admin/crear/categoria/', views.crear_categoria, name='crear_categoria'),
    path('admin/crear/venta/', views.crear_venta_admin, name='crear_venta_admin'),
    path('admin/editar/tipo/<int:id>/', views.editar_tipo_venta, name='editar_tipo_venta'),
    path('admin/editar/categoria/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('admin/eliminar/tipo/<int:id>/', views.eliminar_tipo_venta, name='eliminar_tipo_venta'),
    path('admin/eliminar/categoria/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('admin/tipos/', views.listar_tipos_venta, name='listar_tipos_venta'),
    path('admin/categorias/', views.listar_categorias, name='listar_categorias'),
    path('admin/ventas/editar/<int:venta_id>/', views.editar_venta, name='editar_venta'),
    path('ventas/asignar/', views.asignar_venta_usuario, name='asignar_venta_usuario'),
]
