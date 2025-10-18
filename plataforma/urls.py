from django.urls import path
from .import views
from .views import editar_paciente

app_name = 'plataforma'

urlpatterns = [
    path('pacientes/', views.pacientes, name="pacientes"),
    path('dados_paciente/', views.dados_paciente_listar, name="dados_paciente_listar"),
    path('dados_paciente/<str:id>/', views.dados_paciente, name="dados_paciente"),
    path('editar_paciente/<int:id>/', views.editar_paciente, name='editar_paciente'),
    path('plano_evolucao_listar/', views.plano_evolucao_listar, name="plano_evolucao_listar"),
    path('plano_evolucao/<str:id>/', views.plano_evolucao, name="plano_evolucao"),
    path('evolucao/<str:id>/', views.evolucao, name="evolucao"),
    path('imprimir_paciente/<int:id>/', views.imprimir_paciente, name='imprimir_paciente'),
    path('paciente/<int:paciente_id>/imprimir/', views.imprimir_evolucoes, name='imprimir_evolucoes'),
    path('pacientes/<int:id>/', views.imprimir_dados_paciente, name='imprimir_dados_paciente'),
  

]

