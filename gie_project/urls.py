"""
URL configuration for gie_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from usuarios.views import admin_home, panel_principal
from gie_project.views import  about_view
from . import views


urlpatterns = [
    path('admin/', admin_home, name='index_admin'),
    path('usuarios/', include('usuarios.urls')),
    path('acerca/', about_view, name='about'),
    path('', panel_principal, name='panel_principal'),
    path('fichador/', include('fichador.urls')),  
    path('tareas/', include('tareas.urls')),
    path('reservas/', include('reservas.urls')),
    path('ventas/', include('ventas.urls')),
    path('clientes/', include('clientes.urls')),
    path('stock/', include('stock.urls')),
    path('precios/', views.pagina_precios, name='precios'),
    path('soporte/', views.pagina_soporte, name='soporte'),
]

