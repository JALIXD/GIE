from django.shortcuts import render, redirect, get_object_or_404
from .models import Mesa, FranjaHoraria
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from datetime import datetime, timedelta
import calendar
from django.forms import modelformset_factory
from .models import FranjaHoraria, Reserva 
from django.db.models import Q
from django.contrib import messages
from django.utils.dateparse import parse_date




# verifica si el usuario es admin
def es_admin(user):
    return user.is_authenticated and user.rol == 'admin'

def es_usuario(user):
    return user.is_authenticated and user.rol == 'usuario'

@login_required
def listar_mesas(request):
    mesas = Mesa.objects.all()
    return render(request, 'reservas/listar_mesas.html', {'mesas': mesas})

@login_required
@user_passes_test(es_admin)
def crear_mesa(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        capacidad = request.POST['capacidad']
        Mesa.objects.create(nombre=nombre, capacidad=capacidad)
        return redirect('listar_mesas')
    return render(request, 'reservas/form_mesa.html')

@login_required
@user_passes_test(es_admin)
def editar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    if request.method == 'POST':
        mesa.nombre = request.POST['nombre']
        mesa.capacidad = request.POST['capacidad']
        mesa.save()
        return redirect('listar_mesas')
    return render(request, 'reservas/form_mesa.html', {'mesa': mesa})

@login_required
@user_passes_test(es_admin)
def eliminar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa.delete()
    return redirect('listar_mesas')

@login_required
@user_passes_test(es_admin)
def activar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa.activa = True
    mesa.save()
    return redirect('listar_mesas')

@login_required
@user_passes_test(es_admin)
def desactivar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa.activa = False
    mesa.save()
    return redirect('listar_mesas')


@login_required
@user_passes_test(es_admin)
def crear_franja(request):
    dias = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]

    if request.method == 'POST':
        mesa_id = request.POST['mesa_id']
        dias_semana = request.POST.getlist('dias_semana')
        hora_inicio = request.POST['hora_inicio']
        hora_fin = request.POST['hora_fin']
        duracion = int(request.POST['duracion'])
        recurrente = request.POST.get('recurrente') == 'on'

        mesa = get_object_or_404(Mesa, id=mesa_id)
        fmt = "%H:%M"
        step = timedelta(minutes=duracion)

        for dia in dias_semana:
            start = datetime.strptime(hora_inicio, fmt)
            end = datetime.strptime(hora_fin, fmt)

            while start + step <= end:
                FranjaHoraria.objects.create(
                    mesa=mesa,
                    dia_semana=dia,
                    hora_inicio=start.time(),
                    hora_fin=(start + step).time(),
                    recurrente=recurrente
                )
                start += step

        return redirect('listar_mesas')

    mesa_id = request.GET.get('mesa_id')
    mesa = get_object_or_404(Mesa, id=mesa_id)
    return render(request, 'reservas/form_franja.html', {
        'mesa': mesa,
        'dias': dias
    })

@login_required
def asignar_reservas(request, mesa_id, dia_semana):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    franjas = FranjaHoraria.objects.filter(mesa=mesa, dia_semana=dia_semana).order_by('hora_inicio')

    if request.method == 'POST':
        for franja in franjas:
            cliente = request.POST.get(f'cliente_{franja.id}')
            if cliente:
                Reserva.objects.create(
                    mesa=mesa,
                    franja=franja,
                    cliente=cliente,
                    usuario_asignado=request.user
                )
        return redirect('listar_mesas')

    return render(request, 'reservas/asignar_reservas.html', {
        'mesa': mesa,
        'dia_semana': dia_semana,
        'franjas': franjas,
    })


@login_required
@user_passes_test(es_admin)
def reservar_mesa_individual(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    fecha_actual = request.POST.get('fecha') or request.GET.get('fecha')
    dia_semana = None
    franjas = []

    if fecha_actual:
        fecha_obj = datetime.strptime(fecha_actual, "%Y-%m-%d")
        dia_semana_en = calendar.day_name[fecha_obj.weekday()]
        traduccion = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes',
            'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        dia_semana = traduccion.get(dia_semana_en)

        # Obtener franjas ya reservadas para esa mesa y fecha
        franjas_reservadas = Reserva.objects.filter(
            mesa=mesa,
            fecha_reservada=fecha_obj.date()
        ).values_list('franja_id', flat=True)

        # Excluirlas de las disponibles
        franjas = FranjaHoraria.objects.filter(
            mesa=mesa,
            dia_semana=dia_semana,
            activo=True
        ).exclude(id__in=franjas_reservadas).order_by('hora_inicio')


    if request.method == 'POST' and 'franja_id' in request.POST:
        franja = get_object_or_404(FranjaHoraria, id=request.POST['franja_id'])
        cliente = request.POST['cliente']
        Reserva.objects.create(
            mesa=mesa,
            franja=franja,
            cliente=cliente,
            usuario_asignado=request.user,
            fecha_reservada=fecha_obj.date()
        )

        # Redirige según el rol del usuario
        if request.user.rol == 'admin':
            return redirect('listar_mesas')
        else:
            return redirect('usuario_ver_reservas')

    return render(request, 'reservas/reservar_mesa_individual.html', {
        'mesa': mesa,
        'fecha_actual': fecha_actual,
        'dia_semana': dia_semana,
        'franjas': franjas
    })

@login_required
def reservar_mesa_usuario(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    fecha_actual = request.POST.get('fecha') or request.GET.get('fecha')
    dia_semana = None
    franjas = []

    if fecha_actual:
        fecha_obj = datetime.strptime(fecha_actual, "%Y-%m-%d")
        dia_semana_en = calendar.day_name[fecha_obj.weekday()]
        traduccion = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes',
            'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        dia_semana = traduccion.get(dia_semana_en)

        franjas_reservadas = Reserva.objects.filter(
            mesa=mesa,
            fecha_reservada=fecha_obj.date()
        ).values_list('franja_id', flat=True)

        franjas = FranjaHoraria.objects.filter(
            dia_semana=dia_semana,
            activo=True
        ).exclude(id__in=franjas_reservadas).order_by('hora_inicio')

    if request.method == 'POST' and 'franja_id' in request.POST:
        franja = get_object_or_404(FranjaHoraria, id=request.POST['franja_id'])

        Reserva.objects.create(
            mesa=mesa,
            franja=franja,
            usuario_asignado=request.user,
            fecha_reservada=fecha_obj.date()
        )

        return redirect('usuario_listar_mesas')  # 🔁 URL a donde quieres volver tras reservar

    return render(request, 'reservas/reservar_mesa_usuario.html', {
        'mesa': mesa,
        'fecha_actual': fecha_actual,
        'dia_semana': dia_semana,
        'franjas': franjas
    })

@login_required
def reservar_franja_usuario(request):
    mesas = Mesa.objects.filter(activa=True)

    mesa_id = request.GET.get('mesa_id')
    franjas = FranjaHoraria.objects.filter(mesa_id=mesa_id, activa=True) if mesa_id else FranjaHoraria.objects.none()

    if request.method == 'POST':
        mesa_id = request.POST['mesa_id']
        franja_id = request.POST['franja_id']
        cliente = request.POST['cliente']

        mesa = get_object_or_404(Mesa, id=mesa_id)
        franja = get_object_or_404(FranjaHoraria, id=franja_id)

        Reserva.objects.create(
            mesa=mesa,
            franja=franja,
            cliente=cliente,
            usuario_asignado=request.user
        )
        return redirect('listar_mesas')  # O a una página de éxito

    return render(request, 'reservas/form_reserva_usuario.html', {
        'mesas': mesas,
        'franjas': franjas,
        'mesa_id': mesa_id
    })


@login_required
@user_passes_test(es_admin)
def ver_reservas_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    reservas = Reserva.objects.filter(franja__mesa=mesa).select_related('franja', 'usuario_asignado').order_by('-fecha_reservada')

    # Filtros
    fecha = request.GET.get('fecha')
    cliente = request.GET.get('cliente', '')

    if fecha:
        reservas = reservas.filter(fecha_reservada=parse_date(fecha))
    if cliente:
        reservas = reservas.filter(cliente__icontains=cliente)

    return render(request, 'reservas/ver_reservas_mesa.html', {
        'mesa': mesa,
        'reservas': reservas,
        'fecha': fecha,
        'cliente': cliente
    })

@login_required
@user_passes_test(es_admin)
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    mesa_id = reserva.mesa.id
    reserva.delete()
    return redirect('ver_reservas_mesa', mesa_id=mesa_id)

@login_required
def usuario_listar_mesas(request):
    mesas = Mesa.objects.filter(activa=True)
    return render(request, 'reservas/usuario_listar_mesas.html', {'mesas': mesas})


@login_required
def usuario_ver_reservas(request):
    reservas = Reserva.objects.filter(usuario_asignado=request.user)

    mesa_id = request.GET.get('mesa')
    fecha = request.GET.get('fecha')
    cliente = request.GET.get('cliente')

    if mesa_id:
        reservas = reservas.filter(mesa_id=mesa_id)

    if fecha:
        reservas = reservas.filter(fecha_reservada=fecha)

    if cliente:
        reservas = reservas.filter(cliente__icontains=cliente)

    reservas = reservas.select_related('mesa', 'franja').order_by('-fecha_reservada')

    mesas = Mesa.objects.filter(activa=True)
    return render(request, 'reservas/usuario_reservas.html', {
        'reservas': reservas,
        'mesas': mesas,
    })


@login_required
def ver_reservas_mesa_usuario(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    reservas = Reserva.objects.filter(franja__mesa=mesa).select_related('franja').order_by('-fecha_reserva')

    # Filtros
    fecha = request.GET.get('fecha')
    cliente = request.GET.get('cliente', '')

    if fecha:
        reservas = reservas.filter(fecha_reserva__date=fecha)

    if cliente:
        reservas = reservas.filter(cliente__icontains=cliente)

    if request.method == 'POST':
        reserva_id = request.POST.get('reserva_id')
        reserva = get_object_or_404(Reserva, id=reserva_id, usuario_asignado=request.user)
        reserva.delete()
        messages.success(request, "Reserva cancelada correctamente.")
        return redirect('ver_reservas_mesa_usuario', mesa_id=mesa.id)

    return render(request, 'reservas/ver_reservas_mesa_usuario.html', {
        'mesa': mesa,
        'reservas': reservas,
        'fecha': fecha,
        'cliente': cliente
    })
