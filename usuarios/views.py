from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CustomLoginForm, UserCreationForm
from .models import CustomUser
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from fichador.models import Fichaje
from tareas.models import Tarea
from .forms import UsuarioForm, TareaForm, PerfilUsuarioForm
from django.contrib.auth.forms import PasswordChangeForm


# Función para saber si el usuario es administrador
def es_admin(user):
    return user.is_authenticated and user.rol == 'admin'


# Vista para cerrar sesión y redirigir a la raíz
def logout_view(request):
    logout(request)
    return redirect('/')


# Vista principal según el tipo de usuario
def panel_principal(request):
    if request.user.is_authenticated:
        if request.user.rol == 'admin':
            return redirect('index_admin')
        else:
            return redirect('index_usuario')
    return render(request, 'usuarios/index.html') 


# Vista para usuarios normales (restringida a usuarios logueados)
@login_required
def index_usuario(request):
    return render(request, 'usuarios/index_usuario.html')


# Vista para administradores (restringida a admins)
@user_passes_test(es_admin)
def admin_home(request):
    return render(request, 'usuarios/indexadmin.html')


# Vista de login
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.rol == 'admin':
                return redirect('index_admin')
            else:
                return redirect('/tareas/inicio/')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = CustomLoginForm()
    return render(request, 'usuarios/login.html', {'form': form})


# Vista para que los administradores creen nuevos usuarios
@user_passes_test(es_admin)
def crear_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Encriptar contraseña
            user.save()
            messages.success(request, f"Usuario '{user.username}' creado correctamente.")
            return redirect('index_admin')
    else:
        form = UserCreationForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'usuarios/password_reset.html'
    email_template_name = 'usuarios/password_reset_email.txt'
    subject_template_name = 'usuarios/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

@login_required
def vista_fichaje(request):
    return render(request, 'usuarios/fichaje.html')



@user_passes_test(es_admin)
def panel_usuarios(request):
    usuarios = CustomUser.objects.all()
    return render(request, 'usuarios/admin_usuario.html', {'usuarios': usuarios})


@user_passes_test(es_admin)
def ver_horas_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, pk=user_id)
    fichajes = Fichaje.objects.filter(usuario=usuario).order_by('-timestamp')
    return render(request, 'usuarios/ver_horas_usuario.html', {'usuario': usuario, 'fichajes': fichajes})


@user_passes_test(es_admin)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos del usuario actualizados.")
            return redirect('panel_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


@user_passes_test(es_admin)
def asignar_tareas(request, user_id):
    usuario = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.usuario = usuario
            tarea.save()
            messages.success(request, "Tarea asignada correctamente.")
            return redirect('panel_usuarios')
    else:
        form = TareaForm()
    return render(request, 'usuarios/asignar_tareas.html', {'form': form, 'usuario': usuario})


@login_required
def editar_perfil(request):
    user = request.user
    if request.method == 'POST':
        perfil_form = PerfilUsuarioForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)

        if perfil_form.is_valid() and password_form.is_valid():
            perfil_form.save()
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # para que no cierre sesión
            messages.success(request, 'Perfil y contraseña actualizados correctamente.')
            return redirect('editar_perfil_usuario')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        perfil_form = PerfilUsuarioForm(instance=user)
        password_form = PasswordChangeForm(user)

    return render(request, 'usuarios/editar_perfil.html', {
        'perfil_form': perfil_form,
        'password_form': password_form
    })