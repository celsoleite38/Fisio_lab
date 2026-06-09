from django.shortcuts import redirect
from django.utils import timezone
from django.urls import reverse
from .models import Assinatura

class BloqueioAssinaturaExpiradaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Se o usuário não está logado, deixa navegar pelas páginas públicas (vendas, login, cadastro)
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 2. Evita bloquear o superusuário ou membros da equipe (você trabalhando no sistema)
        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        # 3. Lista de caminhos/URLs que o cliente expirado PRECISA acessar (senão gera loop infinito)
        # Usamos o início do path para capturar sub-rotas ou arquivos estáticos se necessário
        urls_permitidas = [
            reverse('pagina_vendas'),             # Sua view de planos
            '/auth/',                             # Se suas URLs de login/logout começarem com /auth/
            '/admin/',                            # Evita problemas se for testar admin
            '/static/',                           # Deixa carregar o CSS/JS da página de planos
            '/media/',                            # Imagens
        ]

        # Verifica se a URL atual é uma das permitidas
        if any(request.path.startswith(url) for url in urls_permitidas):
            return self.get_response(request)

        # 4. Busca a assinatura válida mais recente deste usuário logado
        # Buscamos tanto por 'usuario' quanto por 'email' para garantir consistência
        assinatura_valida = Assinatura.objects.filter(
            models.Q(usuario=request.user) | models.Q(email=request.user.email),
            status__in=["ativo", "teste"],
            validade__gt=timezone.now()
        ).exists()

        # 5. Se NÃO possui nenhuma assinatura ativa/dentro do prazo, barra o acesso
        if not_assinatura_valida:
            # Redireciona o usuário de volta para a página de vendas/planos
            return redirect('pagina_vendas')

        return self.get_response(request)