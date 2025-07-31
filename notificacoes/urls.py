# notificacoes/urls.py
from django.urls import path
from .views import marcar_aviso_lido, verificar_primeiro_login
from . import views
urlpatterns = [
    path('aviso/lido/<int:pk>/', views.marcar_aviso_lido, name='marcar_aviso_lido'),
    path('verificar-login/', verificar_primeiro_login, name='verificar_primeiro_login'),
]