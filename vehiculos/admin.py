from django.contrib import admin
from .models import User, Vehiculo, Solicitud, Checklist
from django.contrib.auth.admin import UserAdmin

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Rol del Usuario', {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff']

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['patente', 'marca', 'modelo', 'disponible', 'supervisor']
    list_filter = ['disponible', 'supervisor']
    search_fields = ['patente', 'marca', 'modelo']

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ['vehiculo', 'solicitante', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['vehiculo__patente', 'solicitante__username']

@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ['solicitud', 'tipo', 'kilometraje', 'extintor', 'confirmado_por']
    list_filter = ['tipo', 'extintor']
