from datetime import timedelta
#import email
import json
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import Assinatura
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# ──────────────────────────────────────────
# Helpers Asaas
# ──────────────────────────────────────────

ASAAS_HEADERS = {
    'access_token': settings.ASAAS_API_KEY,
    'Content-Type': 'application/json',
}

def _criar_cliente_asaas(nome, email, cpf_cnpj):
    """Cria cliente no Asaas e retorna o ID."""
    url = f"{settings.ASAAS_BASE_URL}/customers"
    payload = {
        "name": nome,
        "email": email,
        "cpfCnpj": cpf_cnpj,   # ← adicionado
    }
    resp = requests.post(url, json=payload, headers=ASAAS_HEADERS)
    resp.raise_for_status()
    return resp.json()['id']


def _criar_cobranca_asaas(customer_id, valor, descricao):
    """Cria cobrança PIX/Boleto e retorna o objeto completo."""
    url = f"{settings.ASAAS_BASE_URL}/payments"
    vencimento = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    payload = {
        "customer": customer_id,
        "billingType": "UNDEFINED",   # UNDEFINED = cliente escolhe PIX ou Boleto
        "value": float(valor),
        "dueDate": vencimento,
        "description": descricao,
    }
    resp = requests.post(url, json=payload, headers=ASAAS_HEADERS)
    resp.raise_for_status()
    return resp.json()


# ──────────────────────────────────────────
# Views
# ──────────────────────────────────────────

def pagina_vendas(request):
    planos = [
        {"nome": "Plano Mensal",     "duracao": "1 mês",   "preco": "R$ 29,90", "link": "pagamento/1-mes"},
        {"nome": "Plano Trimestral", "duracao": "3 meses", "preco": "R$ 79,90", "link": "pagamento/3-meses"},
        {"nome": "Plano Semestral",  "duracao": "6 meses", "preco": "R$ 149,90","link": "pagamento/6-meses"},
        {"nome": "Teste Gratuito",   "duracao": "7 dias",  "preco": "Grátis",   "link": "/teste-gratis/"},
    ]
    return render(request, 'paginas_vendas/pagina_vendas.html', {'planos': planos})




User = get_user_model()

def teste_gratis(request):
    if request.method == 'POST':
        email_usuario = request.POST.get('email', '').strip()

        if not email_usuario:
            return render(request, 'paginas_vendas/erro.html', {
                'mensagem': 'Por favor, informe um e-mail válido.'
            })

        # REGRA 1: Bloqueia se o e-mail já usou o teste grátis histórico
        if Assinatura.objects.filter(email=email_usuario, eh_teste_gratis=True).exists():
            return render(request, 'paginas_vendas/erro.html', {
                'mensagem': 'Este e-mail já utilizou o período de teste gratuito.',
                'email': email_usuario,
                'motivo': 'teste_ja_usado'  # Flag para usar no template se quiser
            })

        # REGRA 2: Bloqueia se o usuário já tem cadastro no sistema
        if User.objects.filter(email=email_usuario).exists():
            return render(request, 'paginas_vendas/erro.html', {
                'mensagem': 'Este e-mail já está cadastrado no sistema.',
                'email': email_usuario,
                'mostrar_assinaturas': True,  # Ativa o botão de ir para planos
                'motivo': 'usuario_existente'
            })

        # FLUXO DE SUCESSO PARA USUÁRIO NOVO:
        # Salva o e-mail na sessão e joga direto para o cadastro para ele criar a conta
        request.session['email_teste'] = email_usuario
        return redirect('/auth/cadastro/')  # Ajuste com a sua URL de cadastro

    return render(request, 'paginas_vendas/teste_gratis_form.html')

def _criar_ou_buscar_cliente(nome, email, cpf_cnpj, phone, 
                              postal_code, address, address_number, province, city):
    url_create = f"{settings.ASAAS_BASE_URL}/customers"
    payload = {
        "name":          nome,
        "email":         email,
        "cpfCnpj":       cpf_cnpj,
        "phone":         phone,
        "postalCode":    postal_code,
        "address":       address,
        "addressNumber": address_number,
        "province":      province,
        "city":          city,
    }
    for k, v in payload.items():
        print(f"  {k}: {type(v)} = {repr(v)}")

    url_create = f"{settings.ASAAS_BASE_URL}/customers"
    resp = requests.post(url_create, json=payload, headers=ASAAS_HEADERS)

    if resp.status_code == 200:
        return resp.json()['id']

    if resp.status_code == 400:
        url_busca = f"{settings.ASAAS_BASE_URL}/customers?cpfCnpj={cpf_cnpj}"
        r = requests.get(url_busca, headers=ASAAS_HEADERS)
        r.raise_for_status()
        data = r.json()
        if data.get('data'):
            return data['data'][0]['id']

    resp.raise_for_status()


def _criar_checkout_asaas(customer_id, valor, descricao, url_sucesso, url_cancelamento):
    
    url = f"{settings.ASAAS_BASE_URL}/checkouts"
    payload = {
        "billingTypes": ["PIX", "CREDIT_CARD"],
        "chargeTypes": ["DETACHED"],
        "name": descricao,
        "value": float(valor),
        "minutesToExpire": 1440,
        "customer": customer_id,
        "items": [                       
            {
                "name": descricao,
                "value": float(valor),
                "quantity": 1,
            }
        ],
        "callback": {
            "successUrl": url_sucesso,
            "cancelUrl": url_cancelamento,
            "autoRedirect": True,
        },
    }
    resp = requests.post(url, json=payload, headers=ASAAS_HEADERS)
    resp.raise_for_status()
    data = resp.json()

    print("Resposta Asaas checkout:", data)

    checkout_url = data.get('link') or data.get('url')  # ← 'link' é o campo correto
    checkout_id  = data.get('id')

    return checkout_url, checkout_id
    checkout_url = data.get('link') or data.get('url')


def checkout(request, plano_slug):
    planos = {
        "1-mes":   {"title": "Plano Mensal",     "price": 29.90,  "dias": 30},
        "3-meses": {"title": "Plano Trimestral", "price": 79.90,  "dias": 90},
        "6-meses": {"title": "Plano Semestral",  "price": 149.90, "dias": 180},
    }

    plano = planos.get(plano_slug)
    if not plano:
        return redirect('pagina_vendas')

    erro = None

    if request.method == 'POST':
        email_usuario  = request.POST.get('email', '').strip()
        nome           = request.POST.get('nome', '').strip()
        cpf_cnpj       = request.POST.get('cpf_cnpj', '').strip()
        phone          = request.POST.get('phone', '').strip()
        postal_code    = request.POST.get('postal_code', '').strip()
        address        = request.POST.get('address', '').strip()
        address_number = request.POST.get('address_number', '').strip()
        province       = request.POST.get('province', '').strip()
        city           = request.POST.get('city', '').strip()

        cpf_cnpj_limpo = ''.join(filter(str.isdigit, cpf_cnpj))
        phone_limpo    = ''.join(filter(str.isdigit, phone))
        postal_limpo   = ''.join(filter(str.isdigit, postal_code))

        if len(cpf_cnpj_limpo) not in (11, 14):
            erro = 'CPF deve ter 11 dígitos ou CNPJ 14 dígitos.'
        else:
            try:
                customer_id = _criar_ou_buscar_cliente(
                    nome=nome,
                    email=email_usuario,
                    cpf_cnpj=cpf_cnpj_limpo,
                    phone=phone_limpo,
                    postal_code=postal_limpo,
                    address=address,
                    address_number=address_number,
                    province=province,
                    city=city,
                )

                url_sucesso      = request.build_absolute_uri('/obrigado/')
                url_cancelamento = request.build_absolute_uri('/planos/')

                checkout_url, checkout_id = _criar_checkout_asaas(
                    customer_id=customer_id,
                    valor=plano['price'],
                    descricao=plano['title'],
                    url_sucesso=url_sucesso,
                    url_cancelamento=url_cancelamento,
                )

                validade = timezone.now() + timedelta(days=plano['dias'])
                Assinatura.objects.create(
                    email=email_usuario,
                    plano=plano['title'],
                    valor=plano['price'],
                    validade=validade,
                    status="pendente",
                    asaas_payment_id=checkout_id or '',
                )

                return redirect(checkout_url)   # ← redireciona para o Asaas

            except requests.exceptions.HTTPError as e:
                erro = f"Erro ao gerar cobrança: {e.response.text}"
            except Exception as e:
                import traceback
                traceback.print_exc()
                erro = f"Erro inesperado: {str(e)}"

    return render(request, 'paginas_vendas/checkout.html', {
        'plano': plano,
        'plano_slug': plano_slug,
        'erro': erro,
    })

def pagina_obrigado(request):
    return render(request, 'paginas_vendas/obrigado.html')


@csrf_exempt
def webhook_asaas(request):
    """Recebe notificações de pagamento do Asaas."""
    if request.method != 'POST':
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
        evento   = data.get('event')
        payment  = data.get('payment', {})
        pay_id   = payment.get('id', '')

        print(f"[WEBHOOK] evento={evento} | payment_id={pay_id}")

        if evento == 'PAYMENT_CONFIRMED' and pay_id:
            Assinatura.objects.filter(
                asaas_payment_id=pay_id
            ).update(status='ativo')
            print(f"[WEBHOOK] Assinaturas ativadas: {atualizadas}")

        elif evento in ('PAYMENT_OVERDUE', 'PAYMENT_DELETED') and pay_id:
            Assinatura.objects.filter(
                asaas_payment_id=pay_id
            ).update(status='cancelado')
            print(f"[WEBHOOK] Assinatura marcada como cancelada: {pay_id}")

        return JsonResponse({"status": "ok"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@staff_member_required
def dashboard_assinaturas(request):
    assinaturas = Assinatura.objects.all().order_by('-data_pagamento')
    return render(request, 'paginas_vendas/dashboard.html', {'assinaturas': assinaturas})


def recursos(request):
    return render(request, 'paginas_vendas/recursos.html')