from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Venta, TipoVenta
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from datetime import datetime
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from clientes.models import Cliente 
from stock.models import Producto, Categoria
from functools import wraps
from django.contrib import messages


User = get_user_model()


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'rol', None) == 'admin':
            return view_func(request, *args, **kwargs)
        return redirect('no_autorizado')  # o lanza un HttpResponseForbidden
    return _wrapped_view

@admin_required
def exportar_pdf(request):
    ventas = filtrar_ventas(request)
    total_ventas = sum(v.total for v in ventas)
    template = get_template('ventas/pdf_ventas.html')
    html = template.render({'ventas': ventas, 'total_ventas': total_ventas})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ventas.pdf"'

    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)
    if pisa_status.err:
        return HttpResponse("Error al generar PDF", status=500)
    return response


def registrar_venta(request):
    if request.method == 'POST':
        tipo_id = request.POST['tipo']
        categoria_id = request.POST['categoria']
        cantidad = request.POST['cantidad']
        comentario = request.POST.get('comentario', '')

        tipo = TipoVenta.objects.get(id=tipo_id)
        categoria = CategoriaVenta.objects.get(id=categoria_id) if categoria_id else None

        Venta.objects.create(
            usuario=request.user,
            tipo=tipo,
            categoria=categoria,
            cantidad=cantidad,
            comentario=comentario
        )
        return redirect('venta_registrada')  # redirige a una página de éxito

    tipos = TipoVenta.objects.filter(activo=True)
    categorias = Categoria.objects.all()
    return render(request, 'ventas/registrar_venta.html', {
        'tipos': tipos,
        'categorias': categorias
    })


@admin_required
def listar_ventas_admin(request):
    ventas = filtrar_ventas(request)
    total_ventas = sum(v.total for v in ventas)

    usuarios = User.objects.all()
    tipos = TipoVenta.objects.all()
    categorias = Categoria.objects.all()  # Nuevo

    return render(request, 'ventas/listar_ventas_admin.html', {
        'ventas': ventas,
        'usuarios': usuarios,
        'tipos': tipos,
        'categorias': categorias,
        'filtros': {
            'usuario': request.GET.get('usuario'),
            'tipo': request.GET.get('tipo'),
            'categoria': request.GET.get('categoria'),
            'desde': request.GET.get('desde'),
            'hasta': request.GET.get('hasta')
        },
        'total_ventas': total_ventas
    })



@admin_required
def crear_tipo_venta(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST.get('descripcion', '')
        TipoVenta.objects.create(nombre=nombre, descripcion=descripcion)
        return redirect('listar_ventas_admin')
    return render(request, 'ventas/form_tipo.html')

@admin_required
def crear_categoria(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST.get('descripcion', '')
        CategoriaVenta.objects.create(nombre=nombre, descripcion=descripcion)
        return redirect('listar_ventas_admin')
    return render(request, 'ventas/form_categoria.html')



@admin_required
def crear_venta_admin(request):
    if request.method == 'POST':
        try:
            usuario_id = request.POST['usuario']
            tipo_id = request.POST['tipo']
            producto_id = request.POST['producto']
            cliente_id = request.POST['cliente']
            cantidad = int(request.POST['cantidad'])
            precio_unitario = float(request.POST['precio_unitario'])
            comentario = request.POST.get('comentario', '')

            usuario = get_user_model().objects.get(id=usuario_id)
            tipo = TipoVenta.objects.get(id=tipo_id)
            producto = Producto.objects.get(id=producto_id)
            cliente = Cliente.objects.get(id=cliente_id)

            # Validar stock
            if cantidad > producto.cantidad_stock:
                from django.contrib import messages
                messages.error(request, "No hay suficiente stock disponible para este producto.")
                return redirect('crear_venta_admin')

            # Crear venta
            Venta.objects.create(
                usuario=usuario,
                cliente=cliente,
                tipo=tipo,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                comentario=comentario
            )

            # Descontar stock
            producto.cantidad_stock -= cantidad
            producto.save()

            return redirect('listar_ventas_admin')

        except Exception as e:
            from django.contrib import messages
            messages.error(request, f"Ocurrió un error al crear la venta: {str(e)}")
            return redirect('crear_venta_admin')

    # Si GET, renderiza formulario
    usuarios = get_user_model().objects.all()
    tipos = TipoVenta.objects.filter(activo=True)
    productos = Producto.objects.select_related('categoria').all()
    categorias = Categoria.objects.all()
    clientes = Cliente.objects.all()

    return render(request, 'ventas/form_venta_admin.html', {
        'usuarios': usuarios,
        'tipos': tipos,
        'productos': productos,
        'categorias': categorias,
        'clientes': clientes
    })


def filtrar_ventas(request):
    ventas = Venta.objects.select_related('usuario', 'tipo', 'producto__categoria').all()

    usuario_id = request.GET.get('usuario')
    tipo_id = request.GET.get('tipo')
    categoria_id = request.GET.get('categoria')
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')

    if usuario_id:
        ventas = ventas.filter(usuario_id=usuario_id)
    if tipo_id:
        ventas = ventas.filter(tipo_id=tipo_id)
    if categoria_id:
        ventas = ventas.filter(producto__categoria_id=categoria_id)
    if fecha_desde:
        ventas = ventas.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        ventas = ventas.filter(fecha__date__lte=fecha_hasta)

    return ventas

@admin_required
def editar_tipo_venta(request, id):
    tipo = TipoVenta.objects.get(id=id)

    if request.method == 'POST':
        tipo.nombre = request.POST['nombre']
        tipo.descripcion = request.POST.get('descripcion', '')
        tipo.save()
        return redirect('listar_ventas_admin')

    return render(request, 'ventas/form_tipo.html', {'tipo': tipo})

@admin_required
def editar_categoria(request, id):
    categoria = CategoriaVenta.objects.get(id=id)

    if request.method == 'POST':
        categoria.nombre = request.POST['nombre']
        categoria.descripcion = request.POST.get('descripcion', '')
        categoria.save()
        return redirect('listar_ventas_admin')

    return render(request, 'ventas/form_categoria.html', {'categoria': categoria})

@admin_required
def eliminar_tipo_venta(request, id):
    tipo = TipoVenta.objects.get(id=id)
    if request.method == 'POST':
        tipo.delete()
        return redirect('listar_ventas_admin')
    return render(request, 'ventas/confirmar_eliminar.html', {'obj': tipo, 'tipo': 'Tipo de Venta'})

@admin_required
def eliminar_categoria(request, id):
    categoria = CategoriaVenta.objects.get(id=id)
    if request.method == 'POST':
        categoria.delete()
        return redirect('listar_ventas_admin')
    return render(request, 'ventas/confirmar_eliminar.html', {'obj': categoria, 'tipo': 'Categoría'})


@admin_required
def listar_tipos_venta(request):
    tipos = TipoVenta.objects.all()
    return render(request, 'ventas/listar_tipos.html', {'tipos': tipos})

@admin_required
def listar_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'ventas/listar_categorias.html', {'categorias': categorias})

@admin_required
def editar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    tipos = TipoVenta.objects.all()
    usuarios = get_user_model().objects.all()
    clientes = Cliente.objects.all()
    categorias = Categoria.objects.prefetch_related('producto_set').all()
    productos = Producto.objects.select_related('categoria').all()

    if request.method == 'POST':
        venta.cliente_id = request.POST.get('cliente')
        venta.usuario_id = request.POST.get('usuario')
        venta.tipo_id = request.POST.get('tipo')
        venta.producto_id = request.POST.get('producto')
        venta.cantidad = request.POST.get('cantidad')
        venta.precio_unitario = request.POST.get('precio_unitario')
        venta.comentario = request.POST.get('comentario')
        venta.save()
        return redirect('listar_ventas_admin')

    return render(request, 'ventas/editar_venta.html', {
        'venta': venta,
        'tipos': tipos,
        'usuarios': usuarios,
        'clientes': clientes,
        'categorias': categorias,
        'productos': productos,
    })

@login_required
def asignar_venta_usuario(request):
    tipos = TipoVenta.objects.all()
    categorias = Categoria.objects.all()
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()

    if request.method == 'POST':
        # Validaciones...
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))

        producto = Producto.objects.filter(id=producto_id).first()
        if not producto:
            messages.error(request, "Producto no válido.")
        elif producto.cantidad_stock < cantidad:
            messages.error(request, f"No hay suficiente stock. Disponible: {producto.cantidad_stock}")
        else:
            # Registrar la venta
            categoria_id = request.POST.get('categoria')
            categoria = Categoria.objects.get(id=categoria_id) if categoria_id else None

            venta = Venta.objects.create(
                usuario=request.user,
                tipo_id=request.POST.get('tipo'),
                producto=producto,
                cliente_id=request.POST.get('cliente'),
                cantidad=cantidad,
                precio_unitario=request.POST.get('precio_unitario'),
                comentario=request.POST.get('comentario')
            )
            producto.cantidad_stock -= cantidad
            producto.save()
            messages.success(request, "Venta registrada correctamente.")
            return redirect('asignar_venta_usuario')

    return render(request, 'ventas/asignar_venta_usuario.html', {
        'tipos': tipos,
        'categorias': categorias,
        'productos': productos,
        'clientes': clientes
    })