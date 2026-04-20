import os
import pandas as pd
import re
from docx import Document

def extrair_dados_fisioterapia(diretorio, nome_fisio):
    lista_pacientes = []
    lista_evolucoes = []

    for arquivo in os.listdir(diretorio):
        if arquivo.endswith(".docx"):
            caminho = os.path.join(diretorio, arquivo)
            try:
                doc = Document(caminho)
                linhas = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
                
                # 1. Configuração padrão do Paciente (evita erros de NOT NULL)
                p_data = {
                    "nome": "", "cpf": "000.000.000-00", "sexo": "Não Informado", 
                    "estadocivil": "Não Informado", "datanascimento": "1900-01-01", 
                    "naturalidade": "Sem Naturalidade", "profissao": "Não Informado", 
                    "email": "", "telefone": "", "endereco": "Sem Endereço", "fisio": nome_fisio
                }
                
                secao_evolucao = False
                
                for i, linha in enumerate(linhas):
                    # Captura Dados Cadastrais
                    if "Nome:" in linha: p_data["nome"] = linha.split(":", 1)[1].strip()
                    elif "Data de nascimento:" in linha:
                        dt = linha.split(":", 1)[1].strip()
                        m = re.search(r"(\d{2})/(\d{2})/(\d{4})", dt)
                        if m: p_data["datanascimento"] = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
                    elif "Naturalidade:" in linha: p_data["naturalidade"] = linha.split(":", 1)[1].strip()
                    elif "Estado civil:" in linha: p_data["estadocivil"] = linha.split(":", 1)[1].strip()
                    elif "Gênero:" in linha: p_data["sexo"] = linha.split(":", 1)[1].strip()
                    elif "Profissão:" in linha: p_data["profissao"] = linha.split(":", 1)[1].strip()
                    elif "Endereço:" in linha: p_data["endereco"] = linha.split(":", 1)[1].strip()

                    # 2. Captura Evoluções
                    if "Evolução" in linha:
                        secao_evolucao = True
                        continue

                    if secao_evolucao:
                        match_data = re.match(r"(\d{2}/\d{2}/\d{2,4})", linha)
                        if match_data:
                            data_sessao = match_data.group(1)
                            conteudo = linha.replace(data_sessao, "").strip()
                            
                            # Pega linhas extras (CD, etc)
                            j = i + 1
                            while j < len(linhas) and not re.match(r"(\d{2}/\d{2}/)", linhas[j]):
                                conteudo += " " + linhas[j]
                                j += 1
                            
                            # Converte data para formato ISO (AAAA-MM-DD) para o banco
                            data_iso = data_sessao
                            m_ev = re.search(r"(\d{2})/(\d{2})/(\d{2,4})", data_sessao)
                            if m_ev:
                                ano = m_ev.group(3)
                                if len(ano) == 2: ano = "20" + ano
                                data_iso = f"{ano}-{m_ev.group(2)}-{m_ev.group(1)}"

                            lista_evolucoes.append({
                                "id": "", 
                                "paciente": p_data["nome"],
                                "titulo": f"Evolução de {data_sessao}",
                                "imagem": "", 
                                "evolucao": conteudo,
                                "data_criacao": data_iso
                            })

                if p_data["nome"]:
                    lista_pacientes.append(p_data)

            except Exception as e:
                print(f"Erro no arquivo {arquivo}: {e}")

    return pd.DataFrame(lista_pacientes), pd.DataFrame(lista_evolucoes)

# --- EXECUÇÃO ---
diretorio = r'/mnt/d/python nutry-lab/evolucoesvanessa'
df_p, df_e = extrair_dados_fisioterapia(diretorio, "vanessarocha")

# Salva os dois arquivos
df_p.to_csv('pacientes_final.csv', index=False, encoding='utf-8-sig')
df_e.to_csv('evolucoes_final.csv', index=False, encoding='utf-8-sig')

print(f"Sucesso! Gerados: 'pacientes_final.csv' ({len(df_p)} pacientes) e 'evolucoes_final.csv' ({len(df_e)} evoluções).")