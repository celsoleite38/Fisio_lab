from django.contrib import admin
from django.urls import path, include
from fisio_lab import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('autenticacao.urls')),
    path('', include('plataforma.urls')),
    path('agenda/', include('agenda.urls',namespace='agenda')),
    path('notificacoes/', include('notificacoes.urls')),
    path('', include('paginas_vendas.urls')),  # Página principal como página de vendas
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)