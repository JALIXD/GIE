from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings

def panel_principal(request):
    if request.user.is_authenticated:
        if request.user.rol == 'admin':
            return redirect('index_admin')
        else:
            return redirect('index_usuario')
    return render(request, 'usuarios/index.html')  # público

def es_admin(user):
    return user.is_authenticated and user.rol == 'admin'

def panel_principal(request):
    return render(request, 'index.html')


@user_passes_test(es_admin)
def admin_home(request):
    return render(request, 'usuarios/indexadmin.html')

def about_view(request):
    return render(request, 'about.html')

def pagina_precios(request):
    return render(request, 'precios.html')



def pagina_soporte(request):
    mensaje_enviado = False

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        mensaje = request.POST.get('mensaje')

        asunto = f"Consulta desde la página de soporte - {nombre}"
        cuerpo = f"Nombre: {nombre}\nEmail: {email}\n\nMensaje:\n{mensaje}"

        send_mail(
            subject=asunto,
            message=cuerpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['gieintelligence@gmail.com'], 
            fail_silently=False,
        )

        mensaje_enviado = True

    return render(request, 'soporte.html', {'mensaje_enviado': mensaje_enviado})
