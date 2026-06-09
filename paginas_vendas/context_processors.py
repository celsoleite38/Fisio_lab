# Em: seu_app/context_processors.py
from django.utils import timezone
from .models import Assinatura  # Importa o seu model de assinaturas

def banner_teste_gratis(request):
    # Se o usuário não estiver logado, não exibe nada
    if not request.user.is_authenticated:
        return {}

    # Busca a assinatura de teste deste usuário que esteja ativa
    assinatura_teste = Assinatura.objects.filter(
        usuario=request.user,
        status="teste",
        eh_teste_gratis=True
    ).first()

    if colocar_banner(assinatura_teste):
        agora = timezone.now()
        # Se a assinatura de teste ainda estiver no prazo de validade
        if assinatura_teste.validade > agora:
            diferenca = assinatura_teste.validade - agora
            # days + 1 garante que se faltarem 1 dia e 12 horas, mostre "2 dias"
            dias_restantes = diferenca.days + 1 
            
            return {
                'em_periodo_de_teste': True,
                'dias_restantes_teste': dias_restantes
            }
            
    return {}

def colocar_banner(assinatura):
    return assinatura is not None