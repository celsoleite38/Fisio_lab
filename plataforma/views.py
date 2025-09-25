from collections import defaultdict
from tkinter import Canvas
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from django.urls import reverse
from autenticacao.models import PerfilProfissional
from .models import Pacientes, DadosPaciente, Evolucao
from datetime import date, datetime
from .forms import PacienteForm, EvolucaoForm
#from reportlab.pdfgen import canvas
from django.views.decorators.http import require_GET

@login_required(login_url='/auth/logar/')
def pacientes (request):
    if request.method =="GET":
        pacientes = Pacientes.objects.filter(fisio=request.user)
        return render(request, 'pacientes.html', {'pacientes':pacientes})
    elif request.method == "POST":
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        sexo = request.POST.get('sexo')
        estadocivil = request.POST.get('estadocivil')
        datanascimento = request.POST.get('datanascimento')
        naturalidade = request.POST.get('naturalidade')
        profissao = request.POST.get('profissao')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco')
        
        if (len(nome.strip()) == 0) or (len(sexo.strip()) == 0) or (len(cpf.strip()) == 0) or (len(estadocivil.strip()) == 0) or (len(datanascimento.strip()) == 0) or (len(naturalidade.strip()) == 0) or (len(profissao.strip()) == 0) or (len(email.strip()) == 0) or (len(telefone.strip()) == 0) or (len(endereco.strip()) == 0):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/pacientes/')
        
        pacientes = Pacientes.objects.filter(email=email)
        
        if pacientes.exists():     
                messages.add_message(request, constants.ERROR, 'Já existe um paciente com esse E-mail')
                return redirect('/pacientes/')
        try: 
            p1 = Pacientes(nome=nome,
                                cpf=cpf,
                                sexo=sexo,
                                estadocivil=estadocivil,
                                datanascimento=datanascimento,
                                naturalidade=naturalidade,
                                profissao=profissao,
                                email=email,
                                telefone=telefone,
                                endereco=endereco,
                                fisio=request.user
            )
            
            p1.save()
        
            messages.add_message(request, constants.SUCCESS, 'Paciente Cadastrado com Sucesso')
            return redirect('/pacientes/')
    
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/pacientes/')
    
@login_required(login_url='/auth/logar/')
def dados_paciente_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(fisio=request.user)
        return render(request, 'dados_paciente_listar.html', {'pacientes': pacientes})
    
@login_required(login_url='/auth/logar/')
def dados_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.fisio == request.user:
        messages.add_message(request, constants.ERROR, 'Acesso negado a este PACIENTE. ')
        return redirect('/dados_paciente/')
    if request.method == "GET":
        dados_paciente = DadosPaciente.objects.filter(paciente=paciente)
        return render(request, 'dados_paciente.html', {'paciente': paciente, 'dados_paciente': dados_paciente})
    
    elif request.method == "POST":
        peso = request.POST.get('peso')
        qp = request.POST.get('qp')
        hma = request.POST.get('hma')
        hpp = request.POST.get('hpp')
        antecedentepf = request.POST.get('antecedentepf')
        exame_fisico = request.POST.get('exame_fisico')
        exames_complementares = request.POST.get('exames_complementares')
        diagnostico = request.POST.get('diagnostico')
        plano_terapeutico = request.POST.get('plano_terapeutico')
        data_dadospaciente = request.POST.get('data_dadospaciente') or datetime.date.today()
        if (len(peso.strip()) == 0) or (len(qp.strip()) == 0) or (len(hma.strip()) == 0) or (len(hpp.strip()) == 0) or (len(antecedentepf.strip()) == 0) or (len(exame_fisico.strip()) == 0) or (len(exames_complementares.strip()) == 0) or (len(diagnostico.strip()) == 0) or (len(plano_terapeutico.strip()) == 0):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos, use 0 ou - quando nao houver valor!')
            return redirect('/dados_paciente/')
        
        paciente = DadosPaciente(paciente=paciente,
                                #data=datetime.now(),
                                peso=peso,
                                qp=qp,
                                hma=hma,
                                hpp=hpp,
                                antecedentepf=antecedentepf,
                                exame_fisico=exame_fisico,  
                                exames_complementares=exames_complementares,
                                diagnostico=diagnostico,
                                plano_terapeutico=plano_terapeutico,
                                data_dadospaciente=data_dadospaciente)                        
        paciente.save()
        
        messages.add_message(request, constants.SUCCESS, 'Dados cadastrado com sucesso')
        
        return redirect('/dados_paciente/')
    



@login_required(login_url='/auth/logar/')
def editar_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.fisio == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/pacientes/')
    if request.method == "POST":
        paciente.nome = request.POST.get('nome')
        paciente.cpf = request.POST.get('cpf')
        paciente.sexo = request.POST.get('sexo')
        paciente.estadocivil = request.POST.get('estadocivil')
        paciente.datanascimento = request.POST.get('datanascimento')
        paciente.naturalidade = request.POST.get('naturalidade')
        paciente.profissao = request.POST.get('profissao')
        paciente.email = request.POST.get('email')
        paciente.telefone = request.POST.get('telefone')
        paciente.endereco = request.POST.get('endereco')
        
        if any(len(campo.strip()) == 0 for campo in [
            paciente.nome, paciente.sexo, paciente.estadocivil, paciente.datanascimento,
            paciente.naturalidade, paciente.profissao, paciente.email, paciente.telefone,
            paciente.endereco
        ]):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect(f'/editar_paciente/{id}/')

        try:
            paciente.datanascimento = datetime.strptime(paciente.datanascimento, '%Y-%m-%d').date()
            paciente.save()
            messages.add_message(request, constants.SUCCESS, 'Paciente atualizado com sucesso!')
            return redirect('/pacientes/')
        except:
            messages.add_message(request, constants.ERROR, 'Erro ao atualizar paciente')
            messages.add_message(request, constants.ERROR, 'Data de nascimento inválida')
            return redirect(f'/editar_paciente/{id}/')

    return render(request, 'editar_paciente.html', {'paciente': paciente})
            
            
def plano_evolucao_listar (request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(fisio=request.user)
        return render(request, 'plano_evolucao_listar.html', {'pacientes': pacientes})
    
        
def plano_evolucao(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.fisio == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/plano_evolucao_listar/')
    
    evolucoes = Evolucao.objects.filter(paciente=paciente).order_by("data_criacao")

    evolucoes_por_data = defaultdict(list)
    for evolucao in evolucoes:
        evolucoes_por_data[evolucao.data_criacao].append(evolucao)
    
    

    
    if request.method == "GET":
        r1 = Evolucao.objects.filter(paciente=paciente).order_by("data_criacao")
        o1 = Evolucao.objects.filter(paciente=paciente).values_list('evolucao', flat=True)
        #return render(request, 'plano_evolucao.html', {'paciente': paciente, 'evolucao': r1, 'evolucao': o1})
    
        return render(request, 'plano_evolucao.html', {'paciente': paciente,  'evolucao': r1, 'evolucoes':evolucoes, })

@login_required(login_url='/auth/logar/')
def evolucao(request, id):  #id_paciente
    paciente = get_object_or_404(Pacientes, id=id) 
    if not paciente.fisio == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/dados_evolucao/')
    
     
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        evolucao = request.POST.get ('evolucao')
        data_criacao = request.POST.get('data_criacao') or datetime.date.today() #data_criacao = data_criacao or datetime.date.today()  # define a data padrão se não for fornecida
        if (len(titulo.strip()) == 0) or (len(evolucao.strip()) == 0):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos, use 0 ou - quando nao houver valor!')

        
        
       
        
        r1 = Evolucao(paciente=paciente,
                    titulo=titulo,
                    evolucao=evolucao,
                    data_criacao=datetime.strptime(data_criacao, '%Y-%m-%d').date())
                    
        r1.save()
        
        messages.add_message(request, constants.SUCCESS, 'Evolução Cadastrada')
        return redirect(f'/plano_evolucao/{id}')



def imprimir_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{paciente.nome}.pdf"'

    p = canvas.Canvas(response)

    # Criando uma página para cada paciente
    p.drawString(100, 800, f"Paciente: {paciente.nome}")
    p.drawString(100, 780, f"Sexo: {paciente.sexo}")
    p.drawString(100, 760, f"Estado Civil: {paciente.estadocivil}")
    p.drawString(100, 740, f"Data de Nascimento: {paciente.datanascimento}")
    p.drawString(100, 720, f"Naturalidade: {paciente.naturalidade}")
    p.drawString(100, 700, f"Profissão: {paciente.profissao}")
    p.drawString(100, 680, f"E-mail: {paciente.email}")
    p.drawString(100, 660, f"Telefone: {paciente.telefone}")
    p.drawString(100, 640, f"Endereço: {paciente.endereco}")

    # Finaliza a página
    p.showPage()
    p.save()

    return response


#impressao de relatorio - evoluções
def imprimir_evolucoes(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id)
    perfil = PerfilProfissional.objects.filter(usuario=request.user).first()

    if request.method == 'POST':
        ids_selecionados = request.POST.getlist('evolucoes')
        
        if ids_selecionados:
            evolucoes = Evolucao.objects.filter(id__in=ids_selecionados)
        else:
            evolucoes = Evolucao.objects.filter(paciente=paciente)
        
         # 🔽 Aqui busca o perfil do fisioterapeuta logado
        perfil = PerfilProfissional.objects.filter(usuario=request.user).first()
        
        return render(request, 'relatorio_impressao.html', {
            'paciente': paciente,
            'evolucoes': evolucoes,
            'today': date.today(),
            'perfil': perfil
        })
    
    else:
        evolucoes = Evolucao.objects.filter(paciente=paciente)
        return render(request, 'selecionar_evolucoes.html', {
            'paciente': paciente,
            'evolucoes': evolucoes
        })


@login_required(login_url='/auth/logar/')
def imprimir_dados_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    
    dados_paciente = DadosPaciente.objects.filter(paciente=paciente)
    if not paciente.fisio == request.user:
        messages.add_message(request, constants.ERROR, 'Acesso negado a este PACIENTE. ')
        return redirect('/dados_paciente/')
    if request.method == 'POST':
        # Não há nada a fazer aqui, pois não estamos lidando com formulários
        pass
    else:
        return render(request, 'imprimir_dados_paciente.html', {
            'paciente': paciente,
            'dados_paciente': dados_paciente,
            'today': date.today()
        })

