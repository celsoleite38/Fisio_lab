from django.contrib import admin
from .models import Ativacao, PerfilProfissional

admin.site.register(Ativacao)

@admin.register(PerfilProfissional)
class PerfilProfissionalAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'pode_excluir_evolucoes',
    )