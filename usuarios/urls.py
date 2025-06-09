from django.urls import path
from .views import *
from fichador.views import panel_fichaje
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('inicio/', index_usuario, name='index_usuario'),
    path('admin/', admin_home, name='index_admin'),  
    path('admin/crear-usuario/', crear_usuario, name='crear_usuario'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='usuarios/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'), name='password_reset_complete'),
    path('fichaje/', panel_fichaje, name='fichaje'),
    path('admin/usuarios/', views.panel_usuarios, name='panel_usuarios'),
    path('admin/usuarios/<int:user_id>/horas/', views.ver_horas_usuario, name='ver_horas_usuario'),
    path('admin/usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('admin/usuarios/<int:user_id>/tareas/', views.asignar_tareas, name='asignar_tareas'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil_usuario'),
]
