
# notificacoes/admin.py
from django.contrib import admin
from .models import Aviso, AvisoUsuario
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import AvisoUsuario
from .utils import enviar_whatsapp

@admin.action(description="Enviar aviso aos usuários selecionados")
def enviar_aviso(modeladmin, request, queryset):
    for aviso in queryset:
        usuarios_destino = aviso.usuarios.all() if aviso.usuarios.exists() else User.objects.all()
        for user in usuarios_destino:
            aviso_usuario, created = AvisoUsuario.objects.get_or_create(aviso=aviso, usuario=user)
            if aviso.enviar_email and user.email:
                send_mail(
                    subject=aviso.titulo,
                    message=aviso.mensagem,
                    from_email='seusite@dominio.com',
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            if aviso.enviar_whatsapp:
                enviar_whatsapp(user, aviso)

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'prioridade', 'automatico', 'primeira_vez_login', 'criado_em', 'enviar_email', 'enviar_whatsapp')
    list_filter = ('prioridade', 'automatico', 'primeira_vez_login')
    filter_horizontal = ('usuarios',)
    actions = [enviar_aviso]

@admin.register(AvisoUsuario)
class AvisoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('aviso', 'usuario', 'lido', 'recebido_em')