import requests
from django.conf import settings

HEADERS = {
    'access_token': settings.ASAAS_API_KEY,
    'Content-Type': 'application/json',
}

def criar_cliente_asaas(nome, email, cpf_cnpj):
    """Cria ou recupera cliente no Asaas."""
    url = f"{settings.ASAAS_BASE_URL}/customers"
    payload = {
        "name": nome,
        "email": email,
        "cpfCnpj": cpf_cnpj,
    }
    resp = requests.post(url, json=payload, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()  # retorna dict com 'id' do customer


def criar_cobranca_asaas(customer_id, valor, descricao, vencimento, 
                          billing_type="BOLETO"):
    """
    billing_type: BOLETO | CREDIT_CARD | PIX | UNDEFINED
    vencimento: "YYYY-MM-DD"
    """
    url = f"{settings.ASAAS_BASE_URL}/payments"
    payload = {
        "customer": customer_id,
        "billingType": billing_type,
        "value": float(valor),
        "dueDate": vencimento,
        "description": descricao,
    }
    resp = requests.post(url, json=payload, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()  # contém 'id', 'invoiceUrl', 'bankSlipUrl', 'pixQrCode'


def criar_assinatura_asaas(customer_id, valor, descricao, ciclo="MONTHLY",
                            vencimento=None):
    """
    ciclo: WEEKLY | BIWEEKLY | MONTHLY | QUARTERLY | SEMIANNUALLY | YEARLY
    """
    from datetime import date
    url = f"{settings.ASAAS_BASE_URL}/subscriptions"
    payload = {
        "customer": customer_id,
        "billingType": "BOLETO",
        "value": float(valor),
        "nextDueDate": vencimento or str(date.today()),
        "cycle": ciclo,
        "description": descricao,
    }
    resp = requests.post(url, json=payload, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def consultar_cobranca(payment_id):
    url = f"{settings.ASAAS_BASE_URL}/payments/{payment_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()