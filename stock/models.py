from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.EmailField() 
    notificar_bajo_stock = models.BooleanField(default=False)  
    def __str__(self):
        return self.nombre
        
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    cantidad_stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def stock_bajo(self):
        return self.cantidad_stock <= self.stock_minimo

    def __str__(self):
        return self.nombre
