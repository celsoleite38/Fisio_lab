from agenda.models import Consulta
from twilio.rest import Client
from datetime import datetime, timedelta

def enviar_lembrete_sms():
    consultas = Consulta.objects.filter(
        data_hora__range=(datetime.now(), datetime.now() + timedelta(hours=24)),
        status='confirmado'
    )
    
    for consulta in consultas:
        client = Client('TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN')
        client.messages.create(
            body=f"Lembrete: Consulta em {consulta.data_hora} com {consulta.profissional.get_full_name()}",
            from_='+5511999999999',  # Número Twilio
            to=consulta.paciente.telefone
        )