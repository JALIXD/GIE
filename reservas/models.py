from django.db import models
from django.conf import settings
from datetime import date


class Mesa(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    capacidad = models.PositiveIntegerField()
    activa = models.BooleanField(default=True)  

    def __str__(self):
        return self.nombre

class FranjaHoraria(models.Model):
    DIAS_SEMANA = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]

    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)
    recurrente = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.mesa.nombre} - {self.dia_semana} {self.hora_inicio} - {self.hora_fin}"


class Reserva(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    franja = models.ForeignKey(FranjaHoraria, on_delete=models.CASCADE)
    cliente = models.CharField(max_length=100)
    usuario_asignado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_reserva = models.DateTimeField(auto_now_add=True)  
    fecha_reservada = models.DateField(default=date.today)

    

    def __str__(self):
        return f"Reserva de {self.cliente} en {self.mesa.nombre} - {self.franja}"