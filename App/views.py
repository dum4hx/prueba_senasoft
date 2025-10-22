from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuarios, TipoIdentificacion, Aeropuertos, Vuelos, Reservas, MetodosPago, Pagos, Tiquetes
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
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import uuid

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

@login_required
def mis_reservas(request):
    try:
        usuario = Usuarios.objects.get(user=request.user)
    except Usuarios.DoesNotExist:
        messages.error(request, "Tu cuenta no está asociada a un perfil de usuario.")
        return redirect('inicio')

    # 🔹 Mostrar solo reservas activas (no pagadas)
    reservas = Reservas.objects.filter(fk_usuario=usuario, activo=True)
    return render(request, 'mis_reservas.html', {'reservas': reservas})



@require_POST
@login_required
def procesar_pago(request):
    selected = request.POST.getlist('reservas_seleccionadas')
    if not selected:
        messages.error(request, "No seleccionaste ninguna reserva para pagar.")
        return redirect('mis_reservas')

    usuario = get_object_or_404(Usuarios, user=request.user)
    reservas = Reservas.objects.filter(idReserva__in=selected, fk_usuario=usuario, activo=True)

    total = 0
    for reserva in reservas:
        total += reserva.fk_vuelo.precio  # Asumiendo que el modelo Vuelo tiene 'precio'

    metodos = MetodosPago.objects.filter(activo=True)

    context = {
        'reservas': reservas,
        'total': total,
        'metodos': metodos
    }
    return render(request, 'procesar_pago.html', context)


@require_POST
@login_required
def confirmar_pago(request):
    metodo_id = request.POST.get('metodo_pago')
    selected = request.POST.getlist('reservas_confirmadas')

    if not metodo_id or not selected:
        messages.error(request, "Debes seleccionar un método de pago y al menos una reserva.")
        return redirect('mis_reservas')

    usuario = get_object_or_404(Usuarios, user=request.user)
    metodo = get_object_or_404(MetodosPago, idMetodoPago=metodo_id)
    reservas = Reservas.objects.filter(idReserva__in=selected, fk_usuario=usuario, activo=True)

    total_pagado = 0
    tiquetes_creados = 0

    for reserva in reservas:
        monto = reserva.fk_vuelo.precio  # asumiendo que el vuelo tiene un campo 'precio'

        # ✅ Crear el registro del pago
        pago = Pagos.objects.create(
            fk_metodo_pago=metodo,
            fk_reserva=reserva,
            monto=monto,
            pagado=True
        )

        # ✅ Generar código único para el tiquete
        codigo_tiquete = f"TKT-{uuid.uuid4().hex[:8].upper()}"

        # ✅ Crear el tiquete asociado
        Tiquetes.objects.create(
            fk_pago=pago,
            codigo=codigo_tiquete
        )

        # ✅ Marcar la reserva como inactiva (ya pagada)
        reserva.activo = False
        reserva.save()

        total_pagado += float(monto)
        tiquetes_creados += 1

    messages.success(
        request,
        f"Pago realizado exitosamente por {len(reservas)} reserva(s). "
        f"Se generaron {tiquetes_creados} tiquete(s). Total pagado: ${total_pagado:,.0f}"
    )
    return redirect('mis_vuelos')
@login_required
def mis_vuelos(request):
    usuario = Usuarios.objects.get(user=request.user)
    pagos = Pagos.objects.filter(
        fk_reserva__fk_usuario=usuario,
        pagado=True
    ).select_related(
        'fk_reserva__fk_vuelo',
        'fk_metodo_pago'
    ).order_by('-fecha_pago')

    context = {'pagos': pagos}
    
    return render(request, 'mis_vuelos.html', context)

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from django.contrib.auth.decorators import login_required
from .models import Pagos, Tiquetes

@login_required
def descargar_tiquete_pdf(request, id_pago):
    pago = get_object_or_404(Pagos, idPago=id_pago, pagado=True)
    reserva = pago.fk_reserva
    vuelo = reserva.fk_vuelo
    tiquete = Tiquetes.objects.filter(fk_pago=pago).first()


    # Crear respuesta tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Tiquete_{pago.idPago}.pdf"'

    # Documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Titulo',
        parent=styles['Heading1'],
        alignment=1,
        fontSize=20,
        textColor=colors.HexColor("#0891b2"),
        spaceAfter=20
    )
    normal_style = ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor("#333333"),
        spaceAfter=8
    )
    small_style = ParagraphStyle(
        name='Small',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#666666"),
        alignment=1
    )

    # Encabezado principal
    elements.append(Paragraph("✈️ Tiquete de Vuelo", title_style))
    elements.append(Paragraph(f"Código de Tiquete: <b>{tiquete.codigo if tiquete else 'No generado'}</b>", normal_style))
    elements.append(Spacer(1, 12))

    # Tabla con datos del vuelo
    data = [
        ['Reserva ID', reserva.idReserva],
        ['Usuario', reserva.fk_usuario.nombre],
        ['Vuelo', vuelo.idVuelo],
        ['Origen', str(vuelo.fk_aeropuerto_salida)],
        ['Destino', str(vuelo.fk_aeropuerto_llegada)],
        ['Fecha de Salida', vuelo.fecha_hora_salida.strftime("%Y-%m-%d %H:%M")],
        ['Fecha de Llegada', vuelo.fecha_hora_llegada.strftime("%Y-%m-%d %H:%M")],
        ['Asiento', reserva.asiento],
        ['Método de Pago', pago.fk_metodo_pago.nombre],
        ['Monto', f"${pago.monto:,.0f}"],
        ['Fecha de Pago', pago.fecha_pago.strftime("%Y-%m-%d %H:%M")],
    ]

    table = Table(data, colWidths=[150, 330])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0891b2")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#0891b2")),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#a7f3d0")),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Gracias por viajar con nosotros. ¡Feliz vuelo! 🛫", small_style))

    # Construir PDF
    doc.build(elements)
    return response








