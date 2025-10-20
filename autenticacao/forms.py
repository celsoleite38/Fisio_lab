from django import forms
from .models import PerfilProfissional
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

class PerfilProfissionalForm(forms.ModelForm):
    class Meta:
        model = PerfilProfissional
        fields = ['nome_completo', 'cpf', 'crefito', 'nomeclinica', 'logotipo']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'crefito': forms.TextInput(attrs={'class': 'form-control'}),
            'nomeclinica': forms.TextInput(attrs={'class': 'form-control'}),
            'logotipo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Envia email em HTML para recuperação de senha
        """
        subject = 'Recuperação de Senha - Fisio Innosoft'
        
        # Renderiza o template HTML
        html_content = render_to_string('registration/password_reset_email.html', context)
        
        # Cria o email com alternativa em texto plano
        email = EmailMultiAlternatives(
            subject,
            html_content,  # conteúdo em HTML
            from_email,
            [to_email]
        )
        email.content_subtype = "html"  # Define como HTML
        email.send()