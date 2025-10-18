# 🧠 Fisio Innosoft

Sistema de gestão para fisioterapeutas, com foco em cadastro de pacientes, evolução de atendimentos, relatórios personalizados e integração com plataformas de pagamento.

## 🚀 Funcionalidades

- Cadastro de pacientes
- CAdastro de dados clinicos do paciente
   - Peso, QP, HMA, HPP, ANTECEDENTES PESSOAIS E FAMILIARES, EXAMES FISICOS, EXAMES COMPLEMENTARES DIAGNOSTICO PLANO TERAPEUTICO.
- Registro de evolução dos atendimentos
- Geração de relatórios com:
  - Nome do paciente
  - Data de nascimento
  - Data do atendimento
  - Nome do fisioterapeuta - usuario cadastrado.
  
- Autenticação integrada com: Obs:esta integração ainda esta em desenvolvimento
   - Mercado Pago
- Painel de assinaturas: Obs:esta integração ainda esta em desenvolvimento
  - Planos mensais, trimestrais, semestrais e anuais
  - Webhooks para atualizar status de pagamentos automaticamente
  - Notificações de expiração por painel e e-mail

## 🛠️ Tecnologias utilizadas

- Python / Django
- HTML + CSS
- SQLite (ou PostgreSQL)
- Git e GitHub
- Integrações com APIs de pagamento # Obs:ainda em desenvolvimento

## ⚙️ Como executar o projeto

```bash
# Clone o repositório
git clone https://github.com/celsoleite38/fisio-minas.git

# Acesse a pasta do projeto
cd fisio-minas

# Crie e ative um ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Aplique as migrações
python manage.py migrate

# Execute o servidor de desenvolvimento
python manage.py runserver
