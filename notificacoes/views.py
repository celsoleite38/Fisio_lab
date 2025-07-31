
# notificacoes/views.py
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import AvisoUsuario, Aviso
from django.contrib.auth.models import User

@login_required
def marcar_aviso_lido(request, pk):
    aviso_usuario = get_object_or_404(AvisoUsuario, pk=pk, usuario=request.user)
    aviso_usuario.lido = True
    aviso_usuario.save()
    return redirect(request.META.get('HTTP_REFERER', '/agenda/'))

@login_required
def verificar_primeiro_login(request):
    if not request.user.avisousuario_set.exists():
        avisos = Aviso.objects.filter(primeira_vez_login=True)
        for aviso in avisos:
            AvisoUsuario.objects.get_or_create(aviso=aviso, usuario=request.user)
    return redirect(request.META.get('HTTP_REFERER', '/agenda/'))
