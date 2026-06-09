from django.db import models
from django.contrib.auth.models import User

class Assinatura(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assinaturas',)
    email = models.EmailField()
    plano = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    validade = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ("ativo", "Ativo"),
        ("cancelado", "Cancelado"),
        ("expirado", "Expirado"),
        ("teste", "Teste Gratuito"),
         ("pendente", "Pendente"),
    ])
    data_pagamento = models.DateTimeField(auto_now_add=True)
    eh_teste_gratis = models.BooleanField(default=False)
    asaas_payment_id = models.CharField(      
        max_length=100, blank=True, null=True
    )

    def __str__(self):
        return f"{self.email} - {self.plano} - {self.status}"
    
    @property
    def esta_ativo(self):
        """Verifica se a assinatura ainda é válida."""
        from django.utils import timezone
        return self.status in ("ativo", "teste") and self.validade > timezone.now()

