from django.urls import path
from paginas_vendas import views
from .views import (
    dashboard_assinaturas,
    pagina_vendas,
    pagina_obrigado,
    recursos,
    teste_gratis,
    webhook_asaas,      
    checkout,
)
from django.views.generic import TemplateView

urlpatterns = [
    path('', pagina_vendas, name='pagina_vendas'),
    path('pagamento/<str:plano_slug>/', checkout, name='checkout'),
    path('obrigado/', pagina_obrigado, name='pagina_obrigado'),
    path('webhook/asaas/', webhook_asaas, name='webhook_asaas'),
    path('dashboard/assinaturas/', dashboard_assinaturas, name='dashboard_assinaturas'),
    path('teste-gratis/', teste_gratis, name='teste_gratis'),
    path('teste-gratis/sucesso/', TemplateView.as_view(
        template_name='paginas_vendas/teste_gratis_sucesso.html'
    ), name='teste_gratis_sucesso'),
    path('recursos/', recursos, name='recursos'),
]