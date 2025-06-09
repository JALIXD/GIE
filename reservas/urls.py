from django.urls import path
from . import views

urlpatterns = [

    # Gestión admin
    path('admin/mesas/', views.listar_mesas, name='listar_mesas'),
    path('admin/mesas/crear/', views.crear_mesa, name='crear_mesa'),
    path('admin/mesas/<int:mesa_id>/editar/', views.editar_mesa, name='editar_mesa'),
    path('admin/mesas/<int:mesa_id>/eliminar/', views.eliminar_mesa, name='eliminar_mesa'),
    path('admin/mesas/<int:mesa_id>/activar/', views.activar_mesa, name='activar_mesa'),
    path('admin/mesas/<int:mesa_id>/desactivar/', views.desactivar_mesa, name='desactivar_mesa'),

    # Franjas horarias
    path('admin/mesas/<int:mesa_id>/asignar/<str:dia_semana>/', views.asignar_reservas, name='asignar_reservas'),
    path('admin/franja/crear/', views.crear_franja, name='crear_franja'),

    # Usuarios reservan franjas
    path('usuario/reservar/', views.reservar_franja_usuario, name='reservar_franja_usuario'),
    path('usuario/reservar/mesa/<int:mesa_id>/', views.reservar_mesa_individual, name='reservar_mesa_individual'),

    path('admin/mesa/<int:mesa_id>/reservas/', views.ver_reservas_mesa, name='ver_reservas_mesa'),
    path('admin/reservas/<int:reserva_id>/eliminar/', views.eliminar_reserva, name='eliminar_reserva'),

    path('usuario/mesas/', views.usuario_listar_mesas, name='usuario_listar_mesas'),
    path('usuario/reservar/mesa/<int:mesa_id>/', views.reservar_mesa_individual, name='reservar_mesa_individual'),
    path('usuario/reservas/', views.usuario_ver_reservas, name='usuario_ver_reservas'),
    path('usuario/mesa/<int:mesa_id>/reservar/', views.reservar_mesa_usuario, name='reservar_mesa_usuario'),
    path('usuario/mesas/<int:mesa_id>/reservas/', views.ver_reservas_mesa_usuario, name='ver_reservas_mesa_usuario'),


]
