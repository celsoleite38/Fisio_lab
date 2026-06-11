from django.shortcuts import redirect
from django.utils import timezone
from django.urls import reverse
from .models import Assinatura
from django.db.models import Q

class BloqueioAssinaturaExpiradaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ⚠️ MODO DE TESTES: DESATIVADO EM PRODUÇÃO
        # Enquanto esta linha existir, o middleware não bloqueia ninguém.
        # QUANDO QUISER COLOCAR EM VIGOR, BASTA COMENTAR A LINHA ABAIXO:
        return self.get_response(request)

        # 1. Se o usuário não está logado, deixa navegar pelas páginas públicas
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 2. Evita bloquear o superusuário ou membros da equipe (você trabalhando no sistema)
        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        # 3. Lista de caminhos/URLs permitidas
        # CORREÇÃO: Removi o '/admin/' daqui para que ele também seja bloqueado no futuro
        urls_permitidas = [
            reverse('pagina_vendas'),             # Sua view de planos
            '/auth/',                             # URLs de login/logout
            '/static/',                           # CSS/JS da página de planos
            '/media/',                            # Imagens
        ]

        # Verifica se a URL atual é uma das permitidas
        if any(request.path.startswith(url) for url in urls_permitidas):
            return self.get_response(request)

        # 4. Busca a assinatura válida mais recente deste usuário logado
        assinatura_valida = Assinatura.objects.filter(
            Q(usuario=request.user) | Q(email=request.user.email),
            status__in=["ativo", "teste"],
            validade__gt=timezone.now()
        ).exists()

        # 5. Se NÃO possui nenhuma assinatura ativa/dentro do prazo, barra o acesso
        if not assinatura_valida:
            # Agora, qualquer rota que não esteja na lista permitida (incluindo /admin/)
            # vai cair aqui e redirecionar para a página de vendas
            return redirect('pagina_vendas')

        return self.get_response(request)