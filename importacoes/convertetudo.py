import os
import pandas as pd
import re
from docx import Document

def extrair_dados_fisioterapia(diretorio, nome_fisio):
    lista_pacientes = []
    lista_evolucoes = []
    lista_dados_clinicos = []

    for arquivo in os.listdir(diretorio):
        if not arquivo.endswith(".docx"): continue
        caminho = os.path.join(diretorio, arquivo)
        try:
            doc = Document(caminho)
            linhas = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            texto_completo = "\n".join(linhas)
            
            # 1. CADASTRO (Pacientes)
            p_data = {
                "nome": "", "cpf": "000.000.000-00", "sexo": "Não Informado", 
                "estadocivil": "Não Informado", "datanascimento": "1900-01-01", 
                "naturalidade": "Sem Naturalidade", "profissao": "Não Informado", 
                "email": "", "telefone": "", "endereco": "Sem Endereço", "fisio": nome_fisio
            }
            
            # 2. ANAMNESE (DadosPaciente)
            clinico = {
                "paciente": "", 
                "peso": 1,  
                "qp": "", "hma": "", "hpp": "", 
                "antecedentepf": "", "exame_fisico": "", 
                "exames_complementares": "", "diagnostico": "", 
                "plano_terapeutico": "", "data_dadospaciente": "1900-01-01"
            }

            def extrair_bloco(inicio, fim, texto, limite):
                padrao = f"{re.escape(inicio)}(.*?){re.escape(fim)}"
                match = re.search(padrao, texto, re.DOTALL | re.IGNORECASE)
                res = match.group(1).strip() if match else ""
                return res[:limite] # Corta para caber no seu CharField do Model

            # Extração respeitando os limites do seu Model
            clinico["qp"] = extrair_bloco("QP:", "HMA", texto_completo, 200)
            clinico["hma"] = extrair_bloco("HMA", "HPP:", texto_completo, 200)
            clinico["hpp"] = extrair_bloco("HPP:", "Antecedentes", texto_completo, 200)
            clinico["antecedentepf"] = extrair_bloco("familiares", "Exame físico", texto_completo, 200)
            clinico["exame_fisico"] = extrair_bloco("Exame físico", "Exames complementares", texto_completo, 200)
            clinico["exames_complementares"] = extrair_bloco("Exames complementares", "Diagnóstico", texto_completo, 200)
            clinico["diagnostico"] = extrair_bloco("Diagnóstico", "Plano terapêutico", texto_completo, 200)
            clinico["plano_terapeutico"] = extrair_bloco("Plano terapêutico", "Evolução", texto_completo, 200)

            for linha in linhas:
                if "Nome:" in linha: 
                    p_data["nome"] = linha.split(":", 1)[1].strip()
                    clinico["paciente"] = p_data["nome"]
                elif "Data de nascimento:" in linha:
                    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", linha)
                    if m: p_data["datanascimento"] = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"

            # 3. EVOLUÇÕES
            secao_evolucao = False
            for i, linha in enumerate(linhas):
                if "Evolução" in linha: secao_evolucao = True; continue
                if secao_evolucao:
                    m_ev = re.match(r"(\d{2}/\d{2}/\d{2,4})", linha)
                    if m_ev:
                        data_s = m_ev.group(1)
                        cont = linha.replace(data_s, "").strip()
                        j = i + 1
                        while j < len(linhas) and not re.match(r"(\d{2}/\d{2}/)", linhas[j]):
                            cont += " " + linhas[j]; j += 1
                        
                        ev_data_iso = data_s
                        m_iso = re.search(r"(\d{2})/(\d{2})/(\d{2,4})", data_s)
                        if m_iso:
                            ano = m_iso.group(3)
                            if len(ano) == 2: ano = "20" + ano
                            ev_data_iso = f"{ano}-{m_iso.group(2)}-{m_iso.group(1)}"

                        lista_evolucoes.append({
                            "id": "", "paciente": p_data["nome"], "titulo": f"Evolução de {data_s}",
                            "imagem": "", "evolucao": cont, "data_criacao": ev_data_iso
                        })

            if p_data["nome"]:
                lista_pacientes.append(p_data)
                lista_dados_clinicos.append(clinico)

        except Exception as e: print(f"Erro em {arquivo}: {e}")

    return pd.DataFrame(lista_pacientes), pd.DataFrame(lista_evolucoes), pd.DataFrame(lista_dados_clinicos)

# --- EXECUÇÃO ---
diretorio = r'/mnt/d/python nutry-lab/evolucoesvanessa'
df_p, df_e, df_d = extrair_dados_fisioterapia(diretorio, "vanessarocha")

df_p.to_csv('pacientes_final.csv', index=False, encoding='utf-8-sig')
df_e.to_csv('evolucoes_final.csv', index=False, encoding='utf-8-sig')
df_d.to_csv('dados_paciente_final.csv', index=False, encoding='utf-8-sig')
print("3 CSVs gerados com sucesso!")