from django.contrib import admin
from django.contrib.auth.models import User # Ou o seu modelo de Fisioterapeuta
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Pacientes, DadosPaciente, Evolucao

class PacientesResource(resources.ModelResource):
    # Este widget procura o fisioterapeuta pelo 'username' no banco de dados
    fisio = fields.Field(
        column_name='fisio',
        attribute='fisio',
        widget=ForeignKeyWidget(User, 'username') # Ajuste 'User' para o seu modelo de fisio se necessário
    )

    class Meta:
        model = Pacientes
        import_id_fields = ('nome',)
        # Campos conforme sua imagem de cadastro
        fields = ('nome', 'cpf', 'sexo', 'estadocivil', 'datanascimento', 
                  'naturalidade', 'profissao', 'email', 'telefone', 'endereco', 'fisio')

@admin.register(Pacientes)
class PacientesAdmin(ImportExportModelAdmin):
    resource_class = PacientesResource
    # Exibe o fisioterapeuta na lista do admin para conferência
    list_display = ('nome', 'fisio', 'datanascimento') 
    list_filter = ('fisio',)

# Mantemos o das Evoluções como estava, pois ele vincula ao Paciente
class EvolucaoResource(resources.ModelResource):
    # Vincula o nome do texto ao objeto Paciente no banco
    paciente = fields.Field(
        column_name='paciente',
        attribute='paciente',
        widget=ForeignKeyWidget(Pacientes, 'nome')
    )

    class Meta:
        model = Evolucao
        # IMPORTANTE: Remova 'data' daqui. Use 'data_criacao'
        # O Django usará esses 3 campos para saber se a evolução já foi importada
        import_id_fields = ('paciente', 'data_criacao', 'evolucao')
        
        # Liste os campos EXATAMENTE como aparecem no seu cabeçalho do CSV
        fields = ('id', 'paciente', 'titulo', 'imagem', 'evolucao', 'data_criacao')
        
        skip_unchanged = True
        report_skipped = True
        
@admin.register(Evolucao)
class EvolucaoAdmin(ImportExportModelAdmin):
    resource_class = EvolucaoResource

class DadosPacienteResource(resources.ModelResource):
    paciente = fields.Field(
        column_name='paciente',
        attribute='paciente',
        widget=ForeignKeyWidget(Pacientes, 'nome')
    )

    class Meta:
        model = DadosPaciente
        # Nomes das colunas batendo exatamente com seu model e o CSV
        fields = (
            'id', 'paciente', 'peso', 'qp', 'hma', 'hpp', 
            'antecedentepf', 'exame_fisico', 'exames_complementares', 
            'diagnostico', 'plano_terapeutico', 'data_dadospaciente'
        )
        import_id_fields = ('paciente',)

@admin.register(DadosPaciente)
class DadosPacienteAdmin(ImportExportModelAdmin):
    resource_class = DadosPacienteResource
    list_display = ('paciente', 'data_dadospaciente')
    search_fields = ('paciente__nome',)