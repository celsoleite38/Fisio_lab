from .models import AvisoUsuario

def avisos_nao_lidos(request):
    if request.user.is_authenticated:
        return {
            'avisos_nao_lidos': AvisoUsuario.objects.filter(usuario=request.user, lido=False)
        }
    return {}
