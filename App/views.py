from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuarios, TipoIdentificacion, Aeropuertos, Vuelos, Reservas
from .forms import FormUsuarios
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Usuarios
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
from django.views.decorators.http import require_POST

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
    aeropuertos = Aeropuertos.objects.filter(activo=True)
    vuelos_ida = vuelos_vuelta = None

    # Rango de fechas permitido (máx. 2 meses hacia adelante)
    fecha_hoy = date.today()
    fecha_max = fecha_hoy + timedelta(days=60)

    if request.GET:
        origen = request.GET.get('origen')
        destino = request.GET.get('destino')
        fecha_salida = request.GET.get('fecha_salida')
        fecha_regreso = request.GET.get('fecha_regreso')
        tipo_viaje = request.GET.get('tipo_viaje')

        # --- VUELOS DE IDA ---
        filtros_ida = {}
        if origen:
            filtros_ida['fk_aeropuerto_salida_id'] = origen
        if destino:
            filtros_ida['fk_aeropuerto_llegada_id'] = destino
        if fecha_salida:
            filtros_ida['fecha_hora_salida__date'] = fecha_salida

        vuelos_ida = Vuelos.objects.filter(**filtros_ida, activo=True).order_by('fecha_hora_salida')

        # --- VUELOS DE VUELTA (solo si aplica) ---
        if tipo_viaje == 'ida_vuelta' and fecha_regreso:
            filtros_vuelta = {}
            if destino:
                filtros_vuelta['fk_aeropuerto_salida_id'] = destino
            if origen:
                filtros_vuelta['fk_aeropuerto_llegada_id'] = origen
            if fecha_regreso:
                filtros_vuelta['fecha_hora_salida__date'] = fecha_regreso

            vuelos_vuelta = Vuelos.objects.filter(**filtros_vuelta, activo=True).order_by('fecha_hora_salida')

    return render(request, 'inicio.html', {
        'aeropuertos': aeropuertos,
        'vuelos_ida': vuelos_ida,
        'vuelos_vuelta': vuelos_vuelta,
        'fecha_hoy': fecha_hoy,
        'fecha_max': fecha_max
    })
    
@require_POST
@login_required
def seleccionar_vuelos(request):
    selected = request.POST.getlist('selected_vuelos')
    if not selected:
        messages.error(request, "No seleccionaste ningún vuelo.")
        return redirect('buscar_vuelos')

    vuelos = Vuelos.objects.filter(idVuelo__in=selected, activo=True)
    if not vuelos.exists():
        messages.error(request, "No se encontraron los vuelos seleccionados.")
        return redirect('/')

    return render(request, 'resumen_reserva.html', {'vuelos': vuelos})

@require_POST
@login_required
def confirmar_reserva(request):
    selected_vuelos = request.POST.getlist('vuelos_confirmados')

    if not selected_vuelos:
        messages.error(request, "No hay vuelos seleccionados para confirmar.")
        return redirect('/')

    # Obtener usuario actual autenticado
    try:
        usuario = Usuarios.objects.get(user=request.user)
    except Usuarios.DoesNotExist:
        messages.error(request, "Tu cuenta no está asociada a un perfil de usuario válido.")
        return redirect('/')

    creadas = 0
    errores = []

    for vuelo_id in selected_vuelos:
        vuelo = Vuelos.objects.filter(idVuelo=vuelo_id, activo=True).first()
        if not vuelo:
            errores.append(f"El vuelo con ID {vuelo_id} no existe o no está activo.")
            continue

        # Obtener asiento desde el formulario
        asiento = request.POST.get(f"asiento_{vuelo_id}", "").strip()

        if not asiento:
            errores.append(f"Debes seleccionar un asiento para el vuelo {vuelo_id}.")
            continue

        # Verificar si el asiento ya está reservado por otro usuario
        ocupado = Reservas.objects.filter(fk_vuelo=vuelo, asiento=asiento, activo=True).exists()
        if ocupado:
            errores.append(f"El asiento {asiento} ya está reservado en el vuelo {vuelo_id}.")
            continue

        # Verificar si el usuario ya tiene una reserva activa para ese vuelo
        existe = Reservas.objects.filter(fk_vuelo=vuelo, fk_usuario=usuario, activo=True).exists()
        if existe:
            errores.append(f"Ya tienes una reserva activa para el vuelo {vuelo_id}.")
            continue

        # Crear la reserva
        Reservas.objects.create(
            fk_vuelo=vuelo,
            fk_usuario=usuario,
            asiento=asiento,
            activo=True
        )
        creadas += 1

    # Mensajes finales
    if creadas > 0:
        messages.success(request, f"Se crearon {creadas} reserva(s) correctamente.")
    if errores:
        messages.warning(request, "Algunas reservas no se pudieron crear:\n" + "\n".join(errores))

    return redirect('/')




