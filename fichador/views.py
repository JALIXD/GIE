from django.contrib.auth.decorators import login_required , user_passes_test
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.db.models import Count
from datetime import datetime, timedelta
from .models import Fichaje
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from usuarios.models import CustomUser


@login_required
def panel_fichaje(request):
    usuario = request.user
    mensaje = error = None

    fecha_str = request.GET.get('fecha')
    mes_str = request.GET.get('mes')
    año_str = request.GET.get('año')

    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha = timezone.localtime().date()
    elif mes_str and año_str:
        try:
            fecha = datetime(int(año_str), int(mes_str), 1).date()
        except ValueError:
            fecha = timezone.localtime().date()
    else:
        fecha = timezone.localtime().date()

    mostrar_fichajes = bool(fecha_str)
    fichajes = Fichaje.objects.filter(usuario=usuario, timestamp__date=fecha).order_by('-timestamp')[:10] if mostrar_fichajes else []

    if request.method == 'POST':
        hoy = timezone.localtime().date()
        fichajes_dia = Fichaje.objects.filter(usuario=usuario, timestamp__date=hoy).order_by('timestamp')
        ultimo_fichaje = fichajes_dia.last()
        tipo = request.POST.get('accion')

        def crear_fichaje(tipo):
            nonlocal mensaje
            Fichaje.objects.create(usuario=usuario, tipo=tipo)
            mensaje = f"Fichaje de tipo '{tipo}' registrado correctamente."

        if tipo == 'entrada':
            if ultimo_fichaje and ultimo_fichaje.tipo in ['entrada', 'descanso', 'regreso']:
                error = "Ya has fichado una entrada hoy."
            else:
                crear_fichaje('entrada')
        elif tipo == 'descanso':
            if not fichajes_dia.filter(tipo='entrada').exists():
                error = "No puedes fichar descanso sin haber fichado entrada."
            elif ultimo_fichaje.tipo != 'entrada':
                error = "Solo puedes irte a descanso justo después de una entrada."
            else:
                crear_fichaje('descanso')
        elif tipo == 'regreso':
            if not fichajes_dia.filter(tipo='descanso').exists():
                error = "No puedes regresar sin haber hecho descanso."
            elif ultimo_fichaje.tipo != 'descanso':
                error = "Solo puedes regresar justo después del descanso."
            else:
                crear_fichaje('regreso')
        elif tipo == 'salida':
            if not fichajes_dia.filter(tipo='entrada').exists():
                error = "No puedes salir sin haber entrado."
            elif ultimo_fichaje.tipo in ['entrada', 'regreso']:
                crear_fichaje('salida')
            else:
                error = "Solo puedes salir después de una entrada o regreso de descanso."
        else:
            error = "Tipo de fichaje no reconocido."

    primer_dia_mes = fecha.replace(day=1)
    if fecha.month == 12:
        ultimo_dia_mes = fecha.replace(year=fecha.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        ultimo_dia_mes = fecha.replace(month=fecha.month + 1, day=1) - timedelta(days=1)

    fichajes_mes = Fichaje.objects.filter(usuario=usuario, timestamp__date__range=(primer_dia_mes, ultimo_dia_mes)).annotate(dia=TruncDate('timestamp')).values('dia').annotate(total=Count('id'))
    dias_con_fichajes = [f['dia'].strftime("%Y-%m-%d") for f in fichajes_mes]

    return render(request, 'panel_fichaje.html', {
        'mensaje': mensaje,
        'error': error,
        'fichajes': fichajes,
        'fecha': fecha,
        'dias_con_fichajes': dias_con_fichajes,
        'mes_anterior': fecha.month - 1 or 12,
        'año_anterior': fecha.year - 1 if fecha.month == 1 else fecha.year,
        'mes_siguiente': fecha.month % 12 + 1,
        'año_siguiente': fecha.year + 1 if fecha.month == 12 else fecha.year,
        'mostrar_fichajes': mostrar_fichajes
    })


def es_admin(user):
    return user.is_authenticated and user.rol == 'admin'

@user_passes_test(es_admin)
def ver_horas_de_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    fecha_filtro = request.GET.get('fecha')

    fichajes = Fichaje.objects.filter(usuario=usuario).order_by('timestamp')

    if fecha_filtro:
        fichajes = fichajes.filter(timestamp__date=fecha_filtro)

    total = timedelta()
    entrada = None

    for f in fichajes:
        if f.tipo == 'entrada':
            entrada = f.timestamp
        elif f.tipo == 'salida' and entrada:
            total += f.timestamp - entrada
            entrada = None

    return render(request, 'fichador/ver_horas_usuario.html', {
        'usuario': usuario,
        'fichajes': fichajes,
        'total': total,
        'fecha_filtro': fecha_filtro
    })