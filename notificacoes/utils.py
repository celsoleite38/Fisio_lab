# notificacoes/utils.py
def enviar_whatsapp(user, aviso):
    # Simulação do envio via WhatsApp (ex: integração com API externa como Twilio, WATI etc)
    numero = getattr(user, 'telefone', None)
    if numero:
        print(f"[WHATSAPP] Enviando para {numero}: {aviso.titulo} - {aviso.mensagem}")