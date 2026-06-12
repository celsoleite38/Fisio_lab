from http.client import HTTPResponse

from django.contrib import admin
from django.urls import path, include
from fisio_lab import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

def test_view(request):
    return HTTPResponse("Plataforma URLs funcionando!")

urlpatterns = [
    path('test/', test_view, name="test"),  # URL de teste
    path('admin/', admin.site.urls),
    path('auth/', include('autenticacao.urls')),
    path('', RedirectView.as_view(url='/auth/logar/', permanent=False)),
    path('plataforma/', include('plataforma.urls', namespace='plataforma')),
    path('agenda/', include('agenda.urls',namespace='agenda')),
    path('notificacoes/', include('notificacoes.urls')),
    path('vendas/', include('paginas_vendas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)