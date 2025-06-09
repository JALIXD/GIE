from django.db import models
from usuarios.models import CustomUser

class Tarea(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_limite = models.DateField()
    asignado_a = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tareas')
    completada = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

