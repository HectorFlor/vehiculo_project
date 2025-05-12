from django.db import models
from django.contrib.auth.models import AbstractUser

# Extensión del modelo de usuario
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('chofer', 'Chofer'),
        ('supervisor', 'Supervisor'),
        ('guardia', 'Guardia'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Vehiculo(models.Model):
    patente = models.CharField(max_length=20)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    disponible = models.BooleanField(default=True)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'supervisor'})

    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo}"

class Solicitud(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('finalizado', 'Finalizado'),
    ]
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__in': ['chofer', 'admin']})
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehiculo} - {self.estado} - {self.fecha_solicitud.strftime('%Y-%m-%d')}"

class Checklist(models.Model):
    TIPO_CHOICES = (
        ('salida', 'Salida'),
        ('retorno', 'Retorno'),
    )

    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    kilometraje = models.PositiveIntegerField()
    extintor = models.BooleanField()
    observaciones = models.TextField(blank=True)
    confirmado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='checklists_confirmados')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Checklist {self.tipo} - {self.solicitud}"