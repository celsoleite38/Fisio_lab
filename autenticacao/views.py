from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse, JsonResponse
from .utils import password_is_valid, email_html
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
import os
from django.conf import settings
from .models import Ativacao, PerfilProfissional
from hashlib import sha256
from django.contrib.auth.decorators import login_required
from .forms import PerfilProfissionalForm
from django.views.decorators.csrf import csrf_exempt
#from django.core.mail import send_mail
from django.views import View

from .models import Ativacao  # Import do seu app de autenticação
from paginas_vendas.models import Assinatura 

def cadastro(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        email_fixo = request.session.get('email_teste')
        return render(request, 'cadastro.html', {'email_fixo': email_fixo})
        
    elif request.method == "POST":
        username = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        email_teste = request.session.get('email_teste')
        if email_teste:
            email = email_teste

        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/auth/cadastro')

        # ── Verificações ANTES de gravar no banco ──────────────────────────
        if User.objects.filter(username=username).exists():
            messages.add_message(request, constants.ERROR, 'Este nome de usuário já está em uso.')
            return redirect('/auth/cadastro')

        if User.objects.filter(email=email).exists():
            messages.add_message(request, constants.ERROR, 'Este e-mail já está cadastrado.')
            return redirect('/auth/cadastro')
        # ───────────────────────────────────────────────────────────────────

        try:
            user = User.objects.create_user(
                username=username,
                password=senha,
                email=email,
                is_active=False
            )

            if email_teste:
                Assinatura.objects.create(
                    usuario=user,
                    email=email,
                    plano='teste_gratis',
                    valor=0,
                    validade=timezone.now() + timedelta(days=7),
                    status='teste',
                    eh_teste_gratis=True,
                )
                del request.session['email_teste']
            else:
                Assinatura.objects.filter(email=email, usuario__isnull=True).update(usuario=user)

            token = sha256(f"{username}{email}".encode()).hexdigest()
            Ativacao(token=token, user=user).save()

        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            messages.add_message(request, constants.ERROR, 'Erro interno ao criar conta. Tente novamente.')
            return redirect('/auth/cadastro')

        # ── E-mail tratado FORA do bloco que cria o usuário ───────────────
        try:
            path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
            email_html(path_template, 'Cadastro confirmado', [email], username=username,
                       link_ativacao=f"https://fisio.innosoft.com.br/auth/ativar_conta/{token}")
        except Exception as e:
            print(f"Erro ao enviar e-mail de ativação: {e}")
            # Usuário foi criado com sucesso; avisa mas não bloqueia o fluxo
            messages.add_message(request, constants.WARNING,
                'Conta criada! Porém houve um problema ao enviar o e-mail de ativação. '
                'Use a opção "Reenviar ativação" na tela de login.')

        messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado!')
        messages.add_message(request, constants.SUCCESS, 'Verifique seu e-mail para confirmar seu cadastro.')
        return redirect('/auth/logar')
        
def logar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/plataforma/pacientes/')
        return render(request, 'logar.html')
    elif request.method == "POST":
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')
        
        usuario = auth.authenticate(username=username, password=senha)
        
        if not usuario:
            messages.add_message(request, constants.ERROR, 'Username ou senha inválidos')
            return redirect('/auth/logar')
        else:
            auth.login(request, usuario)
            return redirect('/plataforma/pacientes/')
        
def sair(request):
    auth.logout(request) 
    return redirect('/auth/logar')

def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    if token.ativo:
        messages.add_message(request, constants.WARNING, 'Este TOKEN já foi usado')
        return redirect('/auth/logar')
    
    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()
    token.ativo = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'CONTA ATIVADA COM SUCESSO')
    return redirect('/auth/logar')




@login_required
def editar_perfil_profissional(request):
    perfil, _ = PerfilProfissional.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form = PerfilProfissionalForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('plataforma:pacientes')  # ou qualquer outra página
    else:
        form = PerfilProfissionalForm(instance=perfil)

    return render(request, 'editar_perfil_profissional.html', {'form': form})



class ReenviarAtivacaoView(View):
    def post(self, request):
        email = request.POST.get('email')
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Busca flexível por email ou username
            try:
                usuario = User.objects.get(email=email)
            except User.DoesNotExist:
                usuario = User.objects.get(username=email)
            
            if usuario.is_active:
                return JsonResponse({
                    'success': False,
                    'message': 'Esta conta já está ativa!'
                })
            else:
                # Gera novo token usando o mesmo método do cadastro
                token = sha256(f"{usuario.username}{usuario.email}".encode()).hexdigest()
                
                # Atualiza ou cria o token de ativação
                ativacao, created = Ativacao.objects.get_or_create(
                    user=usuario,
                    defaults={'token': token, 'ativo': False, 'email': usuario.email}
                )
                if not created:
                    ativacao.token = token
                    ativacao.ativo = False
                    ativacao.save()
                
                link_ativacao = f"https://nutri.innosoft.com.br/auth/ativar_conta/{token}/"
                
                # Envia o email
                path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
                email_html(path_template, 'Cadastro confirmado', [usuario.email], 
                          username=usuario.username, link_ativacao=link_ativacao)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Email de ativação reenviado com sucesso! Verifique sua caixa de entrada.'
                })
                
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Email não encontrado em nosso sistema.'
            })
        except Exception as e:
            # Log para diagnóstico (aparece apenas no servidor)
            print(f"Erro no reenvio de ativação para {email}: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Erro ao reenviar email de ativação. Tente novamente.'
            })