from django.contrib import admin
from .models import Assinatura


@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):

    # Colunas exibidas na listagem
    list_display = (
        'email',
        'plano',
        'valor',
        'status',
        'eh_teste_gratis',
        'validade',
        'data_pagamento',
        'asaas_payment_id',
    )

    # Filtros laterais
    list_filter = (
        'status',
        'plano',
        'eh_teste_gratis',
    )

    # Busca por esses campos
    search_fields = (
        'email',
        'plano',
        'asaas_payment_id',
    )

    # Ordenação padrão
    ordering = ('-data_pagamento',)

    # Campos somente leitura
    readonly_fields = (
        'data_pagamento',
        'asaas_payment_id',
    )

    # Ações personalizadas
    actions = ['marcar_ativo', 'marcar_cancelado']

    @admin.action(description='✅ Marcar selecionadas como ATIVO')
    def marcar_ativo(self, request, queryset):
        atualizadas = queryset.update(status='ativo')
        self.message_user(request, f'{atualizadas} assinatura(s) marcadas como ativas.')

    @admin.action(description='❌ Marcar selecionadas como CANCELADO')
    def marcar_cancelado(self, request, queryset):
        atualizadas = queryset.update(status='cancelado')
        self.message_user(request, f'{atualizadas} assinatura(s) canceladas.')