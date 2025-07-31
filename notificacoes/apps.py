
# notificacoes/apps.py
from django.apps import AppConfig

class NotificacoesConfig(AppConfig):
    name = 'notificacoes'

    def ready(self):
        import notificacoes.signals

