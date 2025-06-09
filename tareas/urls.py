from django.urls import path
from . import views
from .views import panel_usuario


urlpatterns = [
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/<int:user_id>/tareas/', views.ver_tareas_usuario, name='ver_tareas_usuario'),
    path('tareas/nueva/<int:user_id>/', views.asignar_tarea, name='asignar_tarea'),  
    path('tareas/editar/<int:tarea_id>/', views.editar_tarea, name='editar_tarea'),
    path('mis-tareas/', views.tareas_usuario, name='tareas_usuario'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('tareas/completar/<int:tarea_id>/', views.marcar_tarea_completada, name='marcar_tarea_completada'),
    path('tarea/<int:tarea_id>/', views.detalle_tarea, name='detalle_tarea'),
    path('tarea/<int:tarea_id>/toggle/', views.toggle_completada, name='toggle_completada'),
    path('inicio/', panel_usuario, name='panel_usuario'),
    path('admin/tareas/<int:tarea_id>/editar/', views.editar_tarea, name='editar_tarea'),
    path('admin/tareas/<int:tarea_id>/eliminar/', views.eliminar_tarea, name='eliminar_tarea'),
]
