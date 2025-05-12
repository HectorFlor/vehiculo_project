from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehiculo, Solicitud, User, Checklist  
from .forms import SolicitudForm, ChecklistForm
from django.utils import timezone
from django.db.models import Q

@login_required
def dashboard(request):
    if request.user.role == 'chofer':
        return redirect('vehiculos:solicitar_vehiculo')
    return render(request, 'vehiculos/dashboard.html')

@login_required
def solicitar_vehiculo(request):
    usuario = request.user

    if usuario.role not in ['chofer', 'admin']:
        messages.error(request, "No tiene permiso para solicitar vehículos.")
        return redirect('vehiculos:dashboard')

    # Validar si el usuario ya tiene una solicitud aprobada y no finalizada
    solicitudes_abiertas = Solicitud.objects.filter(solicitante=usuario, estado='aprobado')
    if solicitudes_abiertas.exists():
        messages.warning(request, "Ya tiene una solicitud activa.")
        return redirect('vehiculos:dashboard')

    # Filtrar vehículos disponibles bajo tus condiciones
    vehiculos_disponibles = Vehiculo.objects.filter(
        disponible=True
    ).exclude(
        solicitud__estado='aprobado'
    ).distinct()

    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.solicitante = usuario
            solicitud.estado = 'pendiente'
            solicitud.save()
            messages.success(request, "Solicitud enviada correctamente.")
            return redirect('vehiculos:dashboard')
    else:
        form = SolicitudForm()
        form.fields['vehiculo'].queryset = vehiculos_disponibles

    return render(request, 'vehiculos/solicitar_vehiculo.html', {
        'form': form,
        'vehiculos_disponibles': vehiculos_disponibles
    })

@login_required
def solicitudes_pendientes(request):
    usuario = request.user

    if usuario.role not in ['supervisor', 'admin']:
        messages.error(request, "No tiene permiso para ver esta página.")
        return redirect('vehiculos:dashboard')

    if usuario.role == 'supervisor':
        # Supervisores solo ven solicitudes de sus vehículos
        solicitudes = Solicitud.objects.filter(
            vehiculo__supervisor=usuario,
            estado='pendiente'
        )
    else:
        # Administradores ven todas las solicitudes pendientes
        solicitudes = Solicitud.objects.filter(estado='pendiente')

    return render(request, 'vehiculos/solicitudes_pendientes.html', {'solicitudes': solicitudes})

@login_required
def aprobar_solicitud(request, solicitud_id):
    usuario = request.user
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)

    if usuario.role == 'supervisor' and solicitud.vehiculo.supervisor != usuario:
        messages.error(request, "No tiene permiso para aprobar esta solicitud.")
        return redirect('vehiculos:solicitudes_pendientes')

    if solicitud.estado != 'pendiente':
        messages.warning(request, "Esta solicitud ya ha sido procesada.")
        return redirect('vehiculos:solicitudes_pendientes')

    # Aprobar la solicitud
    solicitud.estado = 'aprobado'
    solicitud.save()

    # Marcar el vehículo como no disponible
    vehiculo = solicitud.vehiculo
    vehiculo.disponible = False
    vehiculo.save()

    messages.success(request, "Solicitud aprobada exitosamente.")
    return redirect('vehiculos:solicitudes_pendientes')

@login_required
def rechazar_solicitud(request, solicitud_id):
    usuario = request.user
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)

    if usuario.role == 'supervisor' and solicitud.vehiculo.supervisor != usuario:
        messages.error(request, "No tiene permiso para rechazar esta solicitud.")
        return redirect('vehiculos:solicitudes_pendientes')

    if solicitud.estado != 'pendiente':
        messages.warning(request, "Esta solicitud ya ha sido procesada.")
        return redirect('vehiculos:solicitudes_pendientes')

    # Rechazar la solicitud
    solicitud.estado = 'rechazado'
    solicitud.save()

    messages.success(request, "Solicitud rechazada exitosamente.")
    return redirect('vehiculos:solicitudes_pendientes')

@login_required
def solicitudes_aprobadas_chofer(request):
    solicitudes = Solicitud.objects.filter(
        solicitante=request.user,
        estado='aprobado'
    ).order_by('-fecha_solicitud')

    salida_pendiente = []
    retorno_pendiente = []

    for s in solicitudes:
        salida = Checklist.objects.filter(solicitud=s, tipo='salida').first()
        retorno = Checklist.objects.filter(solicitud=s, tipo='retorno').first()

        if not salida:
            salida_pendiente.append(s)
        elif salida and not retorno:
            retorno_pendiente.append(s)

    return render(request, 'vehiculos/solicitudes_aprobadas_chofer.html', {
        'salida_pendiente': salida_pendiente,
        'retorno_pendiente': retorno_pendiente,
    })

@login_required
def completar_checklist_salida(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)

    if request.user != solicitud.solicitante:
        messages.error(request, "No tiene permiso para completar este checklist.")
        return redirect('vehiculos:dashboard')

    if solicitud.estado != 'aprobado':
        messages.warning(request, "La solicitud debe estar aprobada para completar el checklist.")
        return redirect('vehiculos:dashboard')

    if Checklist.objects.filter(solicitud=solicitud, tipo='salida').exists():
        messages.info(request, "Ya ha completado el checklist de salida.")
        return redirect('vehiculos:dashboard')

    if request.method == 'POST':
        form = ChecklistForm(request.POST)
        if form.is_valid():
            checklist = form.save(commit=False)
            checklist.solicitud = solicitud
            checklist.tipo = 'salida'
            checklist.save()
            messages.success(request, "Checklist de salida enviado para verificación.")
            return redirect('vehiculos:dashboard')
    else:
        form = ChecklistForm()

    return render(request, 'vehiculos/completar_checklist.html', {'form': form, 'solicitud': solicitud})


@login_required
def verificar_checklist_guardia(request):
    if request.user.role not in ['guardia', 'admin']:
        messages.error(request, "No tiene permiso para esta sección.")
        return redirect('vehiculos:dashboard')

    checklists = Checklist.objects.filter(tipo='salida', confirmado_por__isnull=True)

    return render(request, 'vehiculos/verificar_checklist.html', {'checklists': checklists})


@login_required
def confirmar_checklist(request, checklist_id):
    if request.user.role not in ['guardia', 'admin']:
        messages.error(request, "No tiene permiso para confirmar checklists.")
        return redirect('vehiculos:dashboard')

    checklist = get_object_or_404(Checklist, id=checklist_id)
    checklist.confirmado_por = request.user
    checklist.save()

    messages.success(request, "Checklist confirmado. Vehículo puede salir.")
    return redirect('vehiculos:verificar_checklist')

@login_required
def completar_checklist_retorno(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)

    if request.user != solicitud.solicitante:
        messages.error(request, "No tiene permiso para completar este checklist.")
        return redirect('vehiculos:dashboard')

    if solicitud.estado != 'aprobado':
        messages.warning(request, "Solo puede completar el checklist de vehículos aprobados.")
        return redirect('vehiculos:dashboard')

    if Checklist.objects.filter(solicitud=solicitud, tipo='retorno').exists():
        messages.info(request, "Ya ha completado el checklist de retorno.")
        return redirect('vehiculos:dashboard')

    if request.method == 'POST':
        form = ChecklistForm(request.POST)
        if form.is_valid():
            checklist = form.save(commit=False)
            checklist.solicitud = solicitud
            checklist.tipo = 'retorno'
            checklist.save()
            messages.success(request, "Checklist de retorno enviado para verificación.")
            return redirect('vehiculos:dashboard')
    else:
        form = ChecklistForm()

    return render(request, 'vehiculos/completar_checklist.html', {
        'form': form,
        'solicitud': solicitud,
        'tipo': 'retorno'
    })


@login_required
def verificar_checklist_retorno_guardia(request):
    if request.user.role not in ['guardia', 'admin']:
        messages.error(request, "No tiene permiso para esta sección.")
        return redirect('vehiculos:dashboard')

    checklists = Checklist.objects.filter(tipo='retorno', confirmado_por__isnull=True)

    return render(request, 'vehiculos/verificar_checklist_retorno.html', {'checklists': checklists})


@login_required
def confirmar_checklist_retorno(request, checklist_id):
    if request.user.role not in ['guardia', 'admin']:
        messages.error(request, "No tiene permiso para confirmar checklists.")
        return redirect('vehiculos:dashboard')

    checklist = get_object_or_404(Checklist, id=checklist_id)
    checklist.confirmado_por = request.user
    checklist.save()

    # Hacer que el vehículo vuelva a estar disponible
    solicitud = checklist.solicitud
    vehiculo = solicitud.vehiculo
    vehiculo.disponible = True
    vehiculo.save()
    solicitud.estado = 'finalizado'
    solicitud.save()

    messages.success(request, "Checklist confirmado. Vehículo devuelto correctamente.")
    return redirect('vehiculos:verificar_checklist_retorno')