# notificacoes/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Aviso, AvisoUsuario
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .utils import enviar_whatsapp

@receiver(post_save, sender=Aviso)
def enviar_emails_aviso(sender, instance, created, **kwargs):
    if created:
        usuarios_destino = instance.usuarios.all() if instance.usuarios.exists() else User.objects.all()
        for user in usuarios_destino:
            aviso_usuario, _ = AvisoUsuario.objects.get_or_create(aviso=instance, usuario=user)
            if instance.enviar_email and user.email:
                send_mail(
                    subject=instance.titulo,
                    message=instance.mensagem,
                    from_email='seusite@dominio.com',
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            if instance.enviar_whatsapp:
                enviar_whatsapp(user, instance)