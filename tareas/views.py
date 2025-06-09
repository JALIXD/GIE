from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_POST
from .models import Tarea
from .forms import TareaForm, UserEditForm
from usuarios.models import CustomUser

def es_admin(user):
    return user.is_authenticated and user.rol == 'admin'

@user_passes_test(es_admin)
def listar_usuarios(request):
    q = request.GET.get('q', '')
    rol = request.GET.get('rol', '')

    usuarios = CustomUser.objects.all()

    if q:
        usuarios = usuarios.filter(username__icontains=q) | usuarios.filter(first_name__icontains=q) | usuarios.filter(last_name__icontains=q)

    if rol:
        usuarios = usuarios.filter(rol=rol)

    return render(request, 'tareas/listar_usuarios.html', {
        'usuarios': usuarios,
        'q': q,
        'rol': rol,
    })



@user_passes_test(es_admin)
def ver_tareas_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    tareas = Tarea.objects.filter(asignado_a=usuario)
    return render(request, 'tareas/ver_tareas.html', {'usuario': usuario, 'tareas': tareas})


@user_passes_test(es_admin)
def asignar_tarea(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.asignado_a = usuario
            tarea.save()
            return redirect('ver_tareas_usuario', user_id=usuario.id)
    else:
        form = TareaForm()
    return render(request, 'tareas/asignar_tarea.html', {'form': form, 'usuario': usuario})


@user_passes_test(es_admin)
def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            return redirect('ver_tareas_usuario', user_id=tarea.asignado_a.id)
    else:
        form = TareaForm(instance=tarea)
    return render(request, 'tareas/editar_tarea.html', {'form': form, 'tarea': tarea})


@login_required
def tareas_usuario(request):
    tareas = Tarea.objects.filter(asignado_a=request.user)
    total = tareas.count()
    completadas = tareas.filter(completada=True).count()
    porcentaje = int((completadas / total) * 100) if total > 0 else 0

    return render(request, 'tareas/tareas_usuario.html', {
        'tareas': tareas,
        'porcentaje': porcentaje,
        'completadas': completadas,
        'total': total
    })

@user_passes_test(es_admin)
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    usuario.delete()
    return redirect('listar_usuarios')

@user_passes_test(es_admin)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = UserEditForm(instance=usuario)
    return render(request, 'tareas/editar_usuario.html', {'form': form, 'usuario': usuario})

@login_required
def marcar_tarea_completada(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, asignado_a=request.user)
    if request.method == 'POST':
        tarea.completada = True
        tarea.save()
    return redirect('tareas_usuario')

@login_required
def detalle_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, asignado_a=request.user)
    return render(request, 'tareas/detalle_tarea.html', {'tarea': tarea})

@require_POST
@login_required
def toggle_completada(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, asignado_a=request.user)
    tarea.completada = not tarea.completada
    tarea.save()
    return redirect('detalle_tarea', tarea_id=tarea.id)

@login_required
def panel_usuario(request):
    from tareas.models import Tarea

    tareas = Tarea.objects.filter(asignado_a=request.user)
    total = tareas.count()
    completadas = tareas.filter(completada=True).count()
    porcentaje = int((completadas / total) * 100) if total > 0 else 0

    return render(request, 'usuarios/index_usuario.html', {
        'porcentaje': porcentaje,
        'completadas': completadas,
        'total': total
    })

@login_required
@user_passes_test(es_admin)
def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            return redirect('tareas_por_usuario', usuario_id=tarea.usuario.id)
    else:
        form = TareaForm(instance=tarea)
    return render(request, 'tareas/editar_tarea.html', {'form': form, 'tarea': tarea})


@login_required
@user_passes_test(es_admin)
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    usuario_id = tarea.asignado_a.id
    tarea.delete()
    return redirect('ver_tareas_usuario', user_id=tarea.asignado_a.id)

