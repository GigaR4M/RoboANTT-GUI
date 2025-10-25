import pandas as pd
from playwright.sync_api import sync_playwright, Page

# --- Mapas de Configuração (iguais ao seu original) ---

MAPA_SITUACAO = {
    "Brasileiro Maior": "1",
    "Brasileiro Adolescente": "4",
    "Brasileiro Criança": "2",
    "Estrangeiro": "3"
}

MAPA_DOCUMENTOS_BR_ADULTO = {
    "Carteira de Identidade": "1",
    "Carteira Profissional": "2",
    "Registro de Identificação Civil (RIC)": "7",
    "Carteira de Trabalho": "8",
    "Passaporte Brasileiro": "3",
    "Carteira Nacional de Habilitação (CNH)": "9",
    "Autorização de Viagem - FUNAI": "6",
    "CPF": "14"
}

MAPA_DOCUMENTOS_CRIANCA = {
    "Passaporte Brasileiro": "3",
    "Certidão de Nascimento": "5",
    "Carteira de Identidade": "1",
    "Autorização de Viagem (FUNAI)": "6",
    "CPF": "14"
}

MAPA_DOCUMENTOS_ESTRANGEIRO = {
    "Passaporte Estrangeiro": "10",
    "Cédula de Identidade de Estrangeiro (CIE)": "11",
    "Identidade diplomática ou consular": "12",
    "Outro documento legal de viagem": "13"
}

# --- Funções do Robô ---

def fazer_login(pagina: Page, cnpj: str, codigo_acesso: str, placa: str, nsolicitacao: str):
    """
    Realiza o login no sistema da ANTT.
    Agora recebe todos os dados como parâmetros, em vez de ler do .env.
    """
    print("A aceder à página inicial...")
    pagina.goto("https://appweb1.antt.gov.br/autorizacaoDeViagem/AvPublico/inicial.asp")

    # Verificação de segurança para garantir que os dados da UI foram preenchidos
    if not all([cnpj, codigo_acesso, placa, nsolicitacao]):
        print("ERRO CRÍTICO: Todos os campos (CNPJ, Código, Placa, Solicitação) são obrigatórios.")
        return None

    print("A preencher os dados de login...")
    pagina.locator('input[name="txtCNPJ"]').fill(cnpj)
    pagina.locator('input[name="txtPlacaVeiculo"]').fill(placa)
    pagina.locator('input[name="txtCodigoAcesso"]').fill(codigo_acesso)

    print("A entrar no sistema...")
    with pagina.expect_popup() as pagina2_info:
        pagina.get_by_role("button", name="Entrar").click()
    
    pagina2 = pagina2_info.value
    pagina2.wait_for_load_state("domcontentloaded")
    print("Login realizado com sucesso. A navegar para a autorização de viagem...")

    try:
        pagina2.get_by_role("link", name="Autorização de Viagem Comum").click()
        pagina2.get_by_role("row", name="Listar Solicitação/Autorizaçã").get_by_role("button").click()

        print(f"A procurar pela solicitação: {nsolicitacao}")
        pagina2.get_by_role("link", name=nsolicitacao).click()
        pagina2.get_by_role("button", name="Submit").nth(1).click()
        
        pagina2.goto("https://appweb1.antt.gov.br/autorizacaoDeViagem/AvPublico/relacao.asp")
        print("Página de inclusão de passageiros carregada.")
        
        return pagina2
        
    except Exception as e:
        print(f"ERRO ao navegar para a solicitação '{nsolicitacao}'.")
        print("Verifique se o número está correto ou se a página da ANTT mudou.")
        print(f"Detalhe do erro: {e}")
        return None

def adicionar_passageiros(pagina: Page, caminho_csv: str):
    """
    Adiciona os passageiros a partir de um ficheiro CSV, usando lógica para
    selecionar as opções corretas e criando um relatório de falhas.
    """
    try:
        df_passageiros = pd.read_csv(caminho_csv, dtype=str).fillna('')
    except FileNotFoundError:
        print(f"ERRO: O ficheiro {caminho_csv} não foi encontrado.")
        return
    except KeyError as e:
        print(f"ERRO: Coluna {e} não encontrada no CSV. Verifique o cabeçalho do ficheiro.")
        return

    print(f"Encontrados {len(df_passageiros)} passageiros para adicionar.")
    
    # --- IMPLEMENTAÇÃO DA SUGESTÃO 1: Relatório de Falhas ---
    passageiros_com_falha = []

    for indice, passageiro in df_passageiros.iterrows():
        
        # Lê o nome antes do try para usá-lo no 'except'
        nome = passageiro.get("nome", f"LINHA CSV Nº {indice+2}")
        
        try:
            # --- 1. LÊ AS COLUNAS DO CSV ---
            situacao = passageiro["situacao"]
            crianca_de_colo = passageiro["crianca_de_colo"]
            tipo_documento = passageiro["tipo_documento"]
            numero_documento = passageiro["numero_documento"]
            orgao_expedidor = passageiro["orgao_expedidor"]
            ntelefone = passageiro["ntelefone"]
            
            print(f"A adicionar passageiro: {nome} (Situação: {situacao})")

            # --- 2. SELECIONA A SITUAÇÃO ---
            valor_situacao = MAPA_SITUACAO[situacao]
            pagina.locator("#cmbMotivoViagem").select_option(valor_situacao)

            # --- 3. ESCOLHE O MAPA DE DOCUMENTOS CORRETO ---
            mapa_documentos_atual = None
            if situacao in ["Brasileiro Maior", "Brasileiro Adolescente"]:
                mapa_documentos_atual = MAPA_DOCUMENTOS_BR_ADULTO
            elif situacao == "Brasileiro Criança":
                mapa_documentos_atual = MAPA_DOCUMENTOS_CRIANCA
                if crianca_de_colo.lower() == 'sim':
                    print("   -> Marcando como criança de colo.")
                    pagina.locator("input[name=\"IdCriancaColo\"]").check()
            elif situacao == "Estrangeiro":
                mapa_documentos_atual = MAPA_DOCUMENTOS_ESTRANGEIRO
            
            # --- 4. PREENCHE O FORMULÁRIO ---
            valor_documento = mapa_documentos_atual[tipo_documento]
            seletor_documento_dinamico = f"#cmbTipoDocumento{valor_situacao}"
            
            pagina.locator('input[name="txtPassageiro"]').fill(nome)
            pagina.locator(seletor_documento_dinamico).select_option(valor_documento)
            pagina.locator('input[name="txtIdentidade"]').fill(numero_documento)
            pagina.locator('input[name="txtOrgao"]').fill(orgao_expedidor)
            pagina.locator("#telefone").fill(ntelefone)
        
            pagina.locator("#btnInc").click()
            pagina.wait_for_load_state("networkidle")

        except KeyError as e:
            # Adiciona a falha ao relatório
            erro_msg = f"Valor '{e}' não reconhecido. (Verifique 'situacao' ou 'tipo_documento' no CSV)"
            print(f"  ERRO ao processar '{nome}': {erro_msg}")
            passageiros_com_falha.append({'nome': nome, 'erro': erro_msg})
            
            print("  Este passageiro foi ignorado. A recarregar e continuar...")
            pagina.reload()
            continue
            
        except Exception as e:
            # Adiciona a falha ao relatório
            erro_msg = f"Erro inesperado: {e}"
            print(f"  ERRO inesperado ao processar '{nome}': {erro_msg}")
            passageiros_com_falha.append({'nome': nome, 'erro': erro_msg})
            
            print("  Este passageiro foi ignorado. A recarregar e continuar...")
            pagina.reload()
            continue

    print("Processo de adição de passageiros finalizado!")

    # --- IMPRIME O RELATÓRIO FINAL ---
    print("\n" + "="*50)
    print("      RELATÓRIO DE PROCESSAMENTO DA VIAGEM")
    print("="*50)
    
    total_passageiros = len(df_passageiros)
    total_falhas = len(passageiros_com_falha)
    total_sucesso = total_passageiros - total_falhas
    
    print(f"Total de passageiros no CSV: {total_passageiros}")
    print(f"Passageiros adicionados com sucesso: {total_sucesso}")
    print(f"Passageiros que falharam: {total_falhas}")
    
    if total_falhas > 0:
        print("\n--- DETALHES DAS FALHAS ---")
        for i, falha in enumerate(passageiros_com_falha):
            print(f"{i+1}. Passageiro: {falha['nome']}")
            print(f"   Erro: {falha['erro']}\n")
    
    print("="*50 + "\n")


def executar_robo(cnpj: str, codigo_acesso: str, placa_veiculo: str, numero_solicitacao: str, arquivo_passageiros: str):
    """
    Função principal que orquestra a automação.
    Esta função será chamada pela interface gráfica.
    """
    print("A iniciar o robô...")
    
    with sync_playwright() as pw:
        navegador = pw.chromium.launch(headless=False)
        contexto = navegador.new_context()
        pagina_principal = contexto.new_page()

        try:
            pagina_passageiros = fazer_login(pagina_principal, cnpj, codigo_acesso, placa_veiculo, numero_solicitacao)
            
            if pagina_passageiros:
                adicionar_passageiros(pagina_passageiros, arquivo_passageiros)
                print("Processo concluído. O navegador será fechado em 10 segundos.")
                pagina_passageiros.wait_for_timeout(10000)
            else:
                print("Não foi possível continuar devido a uma falha no login ou configuração.")

        except Exception as e:
            print(f"Ocorreu um erro geral durante a execução: {e}")
        finally:
            navegador.close()
            print("Navegador fechado. Pode fechar esta janela.")

# O bloco 'if __name__ == "__main__":' foi removido
# pois este ficheiro agora é um módulo que será importado pelo 'app.py'