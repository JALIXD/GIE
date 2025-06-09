from django.core.mail import send_mail
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Producto , Categoria, Proveedor
from django.db.models import Q
from .forms import ProductoForm, ProveedorForm, CategoriaForm
from django.db import models
from django.contrib import messages



def es_admin(user):
    return user.is_authenticated and user.rol == "admin"

@login_required
def lista_productos(request):
    productos = Producto.objects.all().order_by('-fecha_creacion')
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()

    # 🔍 Filtros
    nombre = request.GET.get('nombre', '')
    categoria_id = request.GET.get('categoria')
    proveedor_id = request.GET.get('proveedor')
    fecha = request.GET.get('fecha')

    if nombre:
        productos = productos.filter(nombre__icontains=nombre)

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if proveedor_id:
        productos = productos.filter(proveedor_id=proveedor_id)

    if fecha:
        productos = productos.filter(fecha_creacion__date=fecha)

    contexto = {
        'productos': productos,
        'categorias': categorias,
        'proveedores': proveedores,
        'nombre': nombre,
        'categoria_id': categoria_id,
        'proveedor_id': proveedor_id,
        'fecha': fecha,
    }

    return render(request, 'stock/lista_productos.html', contexto)

@login_required
@user_passes_test(es_admin)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'stock/formulario_producto.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'stock/formulario_producto.html', {'form': form, 'editar': True})

@login_required
@user_passes_test(es_admin)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    return redirect('lista_productos')


@login_required
@user_passes_test(es_admin)
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            # Enviar correo al proveedor
            send_mail(
                subject='¡Bienvenido como proveedor en GIE!',
                message=f"Hola {proveedor.nombre},\n\nHas sido registrado como proveedor en nuestro sistema. Te contactaremos si alguno de tus productos necesita reposición.",
                from_email=None,  # usa DEFAULT_FROM_EMAIL en settings
                recipient_list=[proveedor.contacto],
                fail_silently=False,
            )
            return redirect('lista_productos')
    else:
        form = ProveedorForm()
    return render(request, 'stock/formulario_proveedor.html', {'form': form})


def verificar_y_notificar_stock_bajo():
    productos_bajo_stock = Producto.objects.filter(cantidad_stock__lte=models.F('stock_minimo'))

    notificados = set()
    for producto in productos_bajo_stock:
        proveedor = producto.proveedor
        if proveedor and proveedor.notificar_bajo_stock and proveedor.contacto and proveedor.id not in notificados:
            send_mail(
                subject="⚠️ Aviso de stock bajo",
                message=f"Estimado/a {proveedor.nombre},\n\nEl producto '{producto.nombre}' se encuentra con bajo stock.\n\nPor favor, revise el inventario.",
                from_email=None,
                recipient_list=[proveedor.contacto],
                fail_silently=True,
            )
            notificados.add(proveedor.id)

@login_required
@user_passes_test(es_admin)
def notificar_stock_proveedores(request):
    verificar_y_notificar_stock_bajo()
    messages.success(request, "Correos de aviso enviados a proveedores con productos en bajo stock.")
    return redirect('lista_productos')

@login_required
@user_passes_test(es_admin)
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'stock/lista_categorias.html', {'categorias': categorias})

@login_required
@user_passes_test(es_admin)
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = CategoriaForm()
    return render(request, 'stock/formulario_categoria.html', {'form': form})
