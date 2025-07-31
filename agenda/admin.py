from django.contrib import admin
from .models import Paciente, Consulta

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email')
    search_fields = ('nome', 'telefone')

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'profissional', 'data_hora', 'status') 
    list_filter = ('status', 'profissional')
    date_hierarchy = 'data_hora' 
    search_fields = ('paciente__nome', 'profissional__username')
    ordering = ('-data_hora',)
