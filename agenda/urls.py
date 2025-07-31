from django.urls import path

from agenda.models import Consulta
from . import views
#from .views import consultas_json, CalendarioView
from .views import (CalendarioView, CriarAgendamentoView, detalhes_consulta, consultas_json, EditarConsultaView, cancelar_consulta_view, RelatorioView)
app_name = 'agenda'

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def webhook_whatsapp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mensagem = data.get('text', '').strip()
        telefone = data.get('from', '')
        
        if mensagem == '1':
            # Atualiza consulta para "confirmado"
            Consulta.objects.filter(paciente__telefone=telefone).update(status='confirmado')
        elif mensagem == '2':
            # Cancela consulta
            Consulta.objects.filter(paciente__telefone=telefone).update(status='cancelado')
        
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)


urlpatterns = [
    path('', CalendarioView.as_view(), name='calendario'),
    path('consultas/', consultas_json, name='consultas_json'),
    path('novo/', CriarAgendamentoView.as_view(), name='novo_agendamento'),
    path('consulta/<int:pk>/', detalhes_consulta, name='detalhes_consulta'),
    path("consulta/<int:pk>/editar/", EditarConsultaView.as_view(), name="editar_consulta"),
    path("consulta/<int:pk>/cancelar/", cancelar_consulta_view, name="cancelar_consulta"), # NOVA ROTA PARA CANCELAMENTO
    #path('relatorio/', RelatorioView.as_view(), name='relatorio'),
    path('relatorio-parcial/', views.relatorio_parcial, name='relatorio_parcial'),

]