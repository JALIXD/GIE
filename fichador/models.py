from django.db import models
from django.conf import settings


class Fichaje(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('descanso', 'Descanso'),
        ('regreso', 'Regreso de descanso'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
