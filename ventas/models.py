from django.db import models
from django.conf import settings
from clientes.models import Cliente
from stock.models import Producto  

class TipoVenta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='compras')
    tipo = models.ForeignKey(TipoVenta, on_delete=models.PROTECT)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)  # ✅ Relación directa con producto
    fecha = models.DateTimeField(auto_now_add=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    comentario = models.TextField(blank=True, null=True)

    @property
    def total(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.usuario.username} → {self.cliente.nombre} | {self.producto.nombre} - {self.total()}€"
