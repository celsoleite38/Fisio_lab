from django.db import models
from django.contrib.auth.models import User

class Ativacao(models.Model):
    token = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ativo = models.BooleanField(default=False)
    email = models.EmailField(max_length=254, default='example@example.com')
    
    def __str__(self):
        return self.user.username


#perfil profissional
class PerfilProfissional(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14)
    crefito = models.CharField(max_length=20)
    nomeclinica = models.CharField(max_length=101, null=True)
    logotipo = models.ImageField(upload_to='logos_profissionais/', blank=True, null=True)
    assinatura = models.ImageField(upload_to='assinaturas/', blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.BooleanField(default=False)
    pode_excluir_evolucoes = models.BooleanField(default=False, verbose_name='Pode excluir evoluções')

    def __str__(self):
        return self.nome_completo


class AlteracaoEmail(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alteracao_email')
    novo_email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} → {self.novo_email}"