from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente
from .forms import ClienteForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from ventas.models import Venta
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

def es_admin(user):
    return user.is_authenticated and user.rol == "admin"

@login_required
@user_passes_test(es_admin)
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista.html', {'clientes': clientes})


@login_required
@user_passes_test(es_admin)
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            
            send_mail(
                subject='Bienvenido a GIE',
                message='Hola {},\n\nBienvenido a GIE, eres un nuevo cliente.'.format(cliente.nombre),
                from_email=None,  # usa DEFAULT_FROM_EMAIL
                recipient_list=[cliente.email],
                fail_silently=False,
            )
            print("Formulario válido, redirigiendo...")
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'clientes/formulario.html', {'form': form})


@login_required
@user_passes_test(es_admin)
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/formulario.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')



@login_required
@user_passes_test(es_admin)
def compras_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    compras = cliente.compras.all()

    # Filtro por fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        compras = compras.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        compras = compras.filter(fecha__date__lte=fecha_fin)

    compras = compras.order_by('-fecha')

    total_gastado = compras.aggregate(
        total=Sum(
            ExpressionWrapper(F('cantidad') * F('precio_unitario'), output_field=DecimalField())
        )
    )['total'] or 0

    return render(request, 'clientes/compras_cliente.html', {
        'cliente': cliente,
        'compras': compras,
        'total_gastado': total_gastado
    })

def exportar_compras_pdf(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    compras = cliente.compras.all()

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        compras = compras.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        compras = compras.filter(fecha__date__lte=fecha_fin)

    total_gastado = compras.aggregate(
        total=Sum(
            ExpressionWrapper(F('cantidad') * F('precio_unitario'), output_field=DecimalField())
        )
    )['total'] or 0

    template = get_template('clientes/pdf_compras.html')
    html = template.render({
        'cliente': cliente,
        'compras': compras,
        'total_gastado': total_gastado,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="compras_{cliente.nombre}.pdf"'

    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)
    if pisa_status.err:
        return HttpResponse("Error al generar PDF", status=500)

    return response