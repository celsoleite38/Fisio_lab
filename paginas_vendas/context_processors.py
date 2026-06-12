from django.utils import timezone
from django.db.models import Q
from .models import Assinatura


def banner_assinatura(request):
    """
    Injeta em todos os templates as variáveis:
    - mostrar_banner_assinatura (bool)
    - dias_restantes_assinatura (int)
    - assinatura_expirada (bool)
    - eh_teste_gratis_assinatura (bool)

    Regra: o banner aparece quando faltam 3 dias ou menos para a
    validade da assinatura (teste ou paga), ou quando ela já expirou.
    """
    if not request.user.is_authenticated:
        return {}

    assinatura = (
        Assinatura.objects.filter(
            Q(usuario=request.user) | Q(email=request.user.email),
            status__in=["ativo", "teste"],
        )
        .order_by('-validade')
        .first()
    )

    if not assinatura:
        return {}

    agora = timezone.now()
    diferenca = assinatura.validade - agora

    # Já expirou
    if diferenca.total_seconds() <= 0:
        return {
            'mostrar_banner_assinatura': True,
            'dias_restantes_assinatura': 0,
            'assinatura_expirada': True,
            'eh_teste_gratis_assinatura': assinatura.eh_teste_gratis,
        }

    # +1 garante que, faltando 1 dia e poucas horas, mostre "2 dias"
    dias_restantes = diferenca.days + 1

    if dias_restantes <= 3:
        return {
            'mostrar_banner_assinatura': True,
            'dias_restantes_assinatura': dias_restantes,
            'assinatura_expirada': False,
            'eh_teste_gratis_assinatura': assinatura.eh_teste_gratis,
        }

    return {}