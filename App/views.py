from django.shortcuts import render, redirect
from .models import Usuarios, TipoIdentificacion
from .forms import FormUsuarios
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Usuarios
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        identificador = request.POST.get('identificador')
        contraseña = request.POST.get('contraseña')

        # 1️⃣ Intentar autenticación como ADMIN (usuario del sistema Django)
        user = authenticate(request, username=identificador, password=contraseña)

        if user is not None:
            login(request, user)
            return redirect('/')  # Redirige a la vista principal o panel

        # 2️⃣ Si no es admin, intentar autenticación como USUARIO del modelo Usuarios
        try:
            usuario = Usuarios.objects.get(numero_identificacion=identificador, activo=True)
        except Usuarios.DoesNotExist:
            usuario = None

        if usuario:
            # Verificamos la contraseña manualmente (ya que está en texto plano en el modelo)
            if usuario.contraseña == contraseña:
                # Autenticar usando el User vinculado
                user = authenticate(request, username=usuario.numero_identificacion, password=contraseña)
                if user:
                    login(request, user)
                    return redirect('/')
                else:
                    messages.error(request, "No se pudo autenticar el usuario vinculado.")
            else:
                messages.error(request, "Contraseña incorrecta.")
        else:
            messages.error(request, "Usuario no encontrado.")

    return render(request, 'login.html')

def registro_view(request):

    tipos_identificacion = TipoIdentificacion.objects.filter(activo=True)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        primer_apellido = request.POST.get('primer_apellido')
        segundo_apellido = request.POST.get('segundo_apellido')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        genero = request.POST.get('genero')
        numero_identificacion = request.POST.get('numero_identificacion')
        tipo_identificacion_id = request.POST.get('tipo_identificacion')
        celular = request.POST.get('celular')
        email = request.POST.get('email')
        contraseña = request.POST.get('contraseña')

        # Validar que no exista el usuario
        if Usuarios.objects.filter(numero_identificacion=numero_identificacion).exists():
            messages.error(request, "Ya existe un usuario con ese número de identificación.")
            return redirect('registro')

        # Crear usuario
        usuario = Usuarios.objects.create(
            nombre=nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            numero_identificacion=numero_identificacion,
            fk_tipo_identificacion_id=tipo_identificacion_id,
            celular=celular,
            email=email,
            contraseña=contraseña
        )

        messages.success(request, "Usuario registrado correctamente")
        return redirect('login')

    return render(request, 'registro.html', {'tipos_identificacion': tipos_identificacion})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def inicio(request):
    return render(request, 'inicio.html')



