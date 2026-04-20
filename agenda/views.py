from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView
from .models import Consulta
from .forms import AgendamentoForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required # Para a função de cancelamento
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.http import require_POST # Para garantir que o cancelamento seja POST
from datetime import datetime, timedelta
import json
from django.conf import settings
from django.contrib.messages import success
from celery import shared_task
from django.core.mail import send_mail
from django.views.generic import TemplateView
from django.template.loader import render_to_string


# Função auxiliar unificada para obter a cor do status
def get_cor_status(status):
    cores = {
        "agendado": "#3498db",
        "confirmado": "#2ecc71",
        "cancelado": "#e74c3c",
        "realizado": "#9b59b6"
    }
    return cores.get(status, "#3498db")

class CriarAgendamentoView(LoginRequiredMixin, CreateView):
    model = Consulta
    form_class = AgendamentoForm
    template_name = "agenda/criar_agendamento.html"
    success_url = reverse_lazy("agenda:calendario")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.profissional = self.request.user
        response = super().form_valid(form)
        
        # ================================================
        # 1. ENVIO IMEDIATO VIA WHATSAPP
        # ================================================
        paciente = form.instance.paciente
        data_formatada = form.instance.data_hora.strftime("%d/%m/%Y às %H:%M")
        
        mensagem_confirmacao = (
            f"*📅 Confirmação de Agendamento - FisioMinas*\n\n"
            f"Olá {paciente.nome},\n\n"
            f"✅ *Consulta agendada com sucesso!*\n"
            f"👨⚕️ Profissional: {form.instance.profissional.get_full_name()}\n"
            f"📆 Data/Hora: {data_formatada}\n"
            f"⏳ Duração: {form.instance.duracao} minutos\n\n"
            f"📍 Local: [Endereço da Clínica]\n\n"
            
        )

        self.enviar_whatsapp(
            telefone=f"55{paciente.telefone}",
            mensagem=mensagem_confirmacao
        )

        # ================================================
        # 2. AGENDAMENTO DO LEMBRETE (2H ANTES)
        # ================================================
        hora_lembrete = form.instance.data_hora - timedelta(hours=2)
        agendar_lembrete.apply_async(
            args=[form.instance.id],
            eta=hora_lembrete
        )

        return response

    def enviar_whatsapp(self, telefone, mensagem):
        """Função auxiliar para envio via WhatsApp"""
        url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_BUSINESS_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": telefone,
            "type": "text",
            "text": {"body": mensagem}
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"Erro WhatsApp: {response.text}")
        except Exception as e:
            print(f"Falha na API WhatsApp: {e}")

# ================================================
# TAREFA CELERY PARA LEMBRETE (RODA 24H ANTES)
# ================================================
@shared_task
def agendar_lembrete(consulta_id):
    from .models import Consulta
    consulta = Consulta.objects.get(id=consulta_id)
    
    if consulta.status == "confirmado":  # Só envia se estiver confirmado
        mensagem = (
            f"*⏰ Lembrete de Consulta - FisioInnosoft*\n\n"
            f"Olá {consulta.paciente.nome},\n\n"
            f"Você tem uma consulta em *24 horas*:\n"
            f"⏰ {consulta.data_hora.strftime('%H:%M')}\n"
            f"👨⚕️ {consulta.profissional.get_full_name()}\n\n"
            f"📍 Local: [Endereço da Clínica]\n"
            f"📞 Contato: [Telefone de Emergência]"
        )
        
        # Reutiliza a função de envio
        
        CriarAgendamentoView().enviar_whatsapp(
            telefone=f"55{consulta.paciente.telefone}",
            mensagem=mensagem
        )
        

class EditarConsultaView(LoginRequiredMixin, UpdateView):
    model = Consulta
    form_class = AgendamentoForm
    template_name = "agenda/editar_consulta.html"

    def get_success_url(self):
        return reverse_lazy("agenda:detalhes_consulta", kwargs={"pk": self.object.pk})

    def get_queryset(self):
        return Consulta.objects.filter(profissional=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

@login_required
@require_POST # Garante que esta view só aceite requisições POST
def cancelar_consulta_view(request, pk):
    try:
        consulta = get_object_or_404(Consulta, pk=pk)

        # Verifica se o usuário logado é o profissional da consulta
        if consulta.profissional != request.user:
            return JsonResponse({"success": False, "message": "Você não tem permissão para cancelar esta consulta."}, status=403)
        
        # Verifica se a consulta já está cancelada ou realizada
        if consulta.status == "cancelado":
            return JsonResponse({"success": False, "message": "Esta consulta já está cancelada."}, status=400)
        if consulta.status == "realizado":
            return JsonResponse({"success": False, "message": "Não é possível cancelar uma consulta já realizada."}, status=400)

        consulta.status = "cancelado" # Define o status como cancelado
        consulta.save()
        return JsonResponse({"success": True, "message": "Consulta cancelada com sucesso!"})

    except Consulta.DoesNotExist:
        return JsonResponse({"success": False, "message": "Consulta não encontrada."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Ocorreu um erro: {str(e)}"}, status=500)
# Fim da função cancelar_consulta_view - Certifique-se de que a próxima função está corretamente desindentada.

def detalhes_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, profissional=request.user)
    return render(request, "agenda/detalhes_consulta.html", {"consulta": consulta})

class CalendarioView(LoginRequiredMixin, TemplateView):
    template_name = "agenda/calendario.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def consultas_json(request):
    consultas = Consulta.objects.filter(profissional=request.user)
    eventos = []
    for consulta in consultas:
        eventos.append({
            "id": consulta.id,
            "title": f"{consulta.paciente.nome} ({consulta.get_status_display()})",
            "start": consulta.data_hora.isoformat(),
            "end": (consulta.data_hora + timedelta(minutes=consulta.duracao)).isoformat(),
            "color": get_cor_status(consulta.status),
            "extendedProps": {
                "paciente_id": consulta.paciente.id,
                "telefone": consulta.paciente.telefone,
                "observacoes": consulta.observacoes,
                "status": consulta.status
            }
        })
    return JsonResponse(eventos, safe=False)

class RelatorioView(LoginRequiredMixin, TemplateView):
    template_name = 'agenda/relatorio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inicio_semana = datetime.now() - timedelta(days=7)
        consultas = Consulta.objects.filter(
            profissional=self.request.user,
            data_hora__gte=inicio_semana
        )
        context['stats'] = {
            'total': consultas.count(),
            'confirmados': consultas.filter(status='confirmado').count(),
            'cancelados': consultas.filter(status='cancelado').count(),
            'ocupacao': (consultas.filter(status='confirmado').count() / consultas.count() * 100) if consultas.count() > 0 else 0,
        }
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('agenda/_relatorio_parcial.html', context, request=self.request)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)


def relatorio_parcial(request):
    inicio_semana = datetime.now() - timedelta(days=7)
    consultas = Consulta.objects.filter(profissional=request.user, data_hora__gte=inicio_semana)

    context = {
        'stats': {
            'total': consultas.count(),
            'confirmados': consultas.filter(status='confirmado').count(),
            'cancelados': consultas.filter(status='cancelado').count(),
            'ocupacao': (consultas.filter(status='confirmado').count() / consultas.count() * 100) if consultas.count() > 0 else 0,
        }
    }
    html = render_to_string('agenda/_relatorio_parcial.html', context)
    return JsonResponse({'html': html})
