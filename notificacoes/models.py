# notificacoes/models.py
from django.db import models
from django.contrib.auth.models import User

class Aviso(models.Model):
    NIVEL_PRIORIDADE = [
        ('info', 'Informativo'),
        ('alerta', 'Alerta'),
        ('erro', 'Erro')
    ]

    titulo = models.CharField(max_length=150)
    mensagem = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    automatico = models.BooleanField(default=False)
    enviar_email = models.BooleanField(default=True)
    enviar_whatsapp = models.BooleanField(default=False)
    primeira_vez_login = models.BooleanField(default=False)
    usuarios = models.ManyToManyField(User, blank=True, related_name='avisos_direcionados')
    prioridade = models.CharField(max_length=10, choices=NIVEL_PRIORIDADE, default='info')

    def __str__(self):
        return self.titulo

class AvisoUsuario(models.Model):
    aviso = models.ForeignKey(Aviso, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    lido = models.BooleanField(default=False)
    recebido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('aviso', 'usuario')

# Create your models here.
