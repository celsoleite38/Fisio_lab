from datetime import date, datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now



class Pacientes(models.Model):
    choices_sexo = (('Feminino', 'Feminino'),
                    ('Masculino', 'Masculino'),
                    ('Outros', 'Outros'))
    choices_estadocivil = (('Casado(a)', 'Casado(a)'),
                    ('Solteiro(a)', 'Solteiro(a)'),
                    ('Divorciado(a)', 'Divorciado(a)'),
                    ('Viuvo(a)', 'Viuvo(a)'))
    nome = models.CharField(max_length=50)
    cpf = models.CharField(max_length=14, verbose_name="CPF", blank=False, null=True)
    sexo = models.CharField(max_length=24, choices=choices_sexo)
    estadocivil = models.CharField(max_length=25, choices=choices_estadocivil)
    datanascimento = models.DateField()
    naturalidade = models.CharField(max_length=120)
    profissao = models.CharField(max_length=50)
    email = models.EmailField()
    telefone = models.CharField(max_length=25)
    endereco = models.CharField(max_length=50)
    fisio = models.ForeignKey(User, on_delete=models.CASCADE)
                                                    #pode ser usar SET_NULL para quando apagar o fisio nao apague os pacientes dele
    def __str__(self):
        return self.nome

class DadosPaciente(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    #data = models.DateField()
    peso = models.IntegerField()
    qp = models.CharField(max_length=125)
    hma = models.CharField(max_length=125)
    hpp = models.CharField(max_length=125)
    antecedentepf = models.CharField(max_length=120)
    exame_fisico = models.CharField(max_length=88)
    exames_complementares = models.CharField(max_length=80)
    diagnostico = models.CharField(max_length=80)
    plano_terapeutico = models.CharField(max_length=80)
    data_dadospaciente = models.DateField()
        
    def __str__(self):
        return f"Paciente({self.paciente.nome}, {self.peso})"
    
class Evolucao(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    imagem = models.ImageField(upload_to="fotos")
    evolucao = models.TextField()
    data_criacao = models.DateField()
    
    def __str__(self):
        return self.evolucao
    
   