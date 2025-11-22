import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import robo  # O nosso ficheiro robo.py continua igual
import threading # Para o robô não "congelar" a interface
import sys
import json
import os

CONFIG_FILE = "config.json"

def load_config():
    """
    Carrega as credenciais do arquivo de configuração se existir.
    Retorna uma tupla (cnpj, codigo_acesso, lembrar) ou (None, None, False).
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get("cnpj", ""), data.get("codigo_acesso", ""), True
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    return "", "", False

def save_config(cnpj, codigo_acesso):
    """
    Salva as credenciais no arquivo de configuração.
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"cnpj": cnpj, "codigo_acesso": codigo_acesso}, f)
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")

def delete_config():
    """
    Remove o arquivo de configuração se existir.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
        except Exception as e:
            print(f"Erro ao remover configurações: {e}")

class PrintRedirector:
    """
    Uma classe para redirecionar os 'prints' do robô 
    para a caixa de texto (log) na interface.
    """
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        # Insere o texto no widget e garante que a última linha apareça
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END) # Rola para o fim

    def flush(self):
        # O 'print' precisa desta função, mesmo que não faça nada
        pass

def iniciar_robo():
    """
    Função chamada quando o botão "Executar" é clicado.
    Valida os dados e inicia o robô numa thread separada.
    """
    
    # --- 1. Ler os valores dos campos ---
    cnpj = cnpj_var.get()
    codigo_acesso = codigo_acesso_var.get()
    placa = placa_var.get()
    solicitacao = solicitacao_var.get()
    ficheiro_csv = ficheiro_var.get()
    lembrar = lembrar_var.get()

    # --- 1.1 Salvar ou Esquecer Credenciais ---
    if lembrar:
        save_config(cnpj, codigo_acesso)
    else:
        delete_config()

    # --- 2. Validar os dados ---
    if not all([cnpj, codigo_acesso, placa, solicitacao, ficheiro_csv]):
        messagebox.showerror("Erro", "Todos os campos são obrigatórios! Por favor, preencha tudo.")
        return # Para a execução

    # --- 3. Preparar a interface para execução ---
    # Limpa o log anterior
    log_box.config(state=tk.NORMAL) # Precisa estar "normal" para apagar
    log_box.delete("1.0", tk.END)
    log_box.config(state=tk.DISABLED) # Desativa para o utilizador não escrever
    
    # Desativa o botão
    exec_button.config(state=tk.DISABLED, text="A Executar...")

    # --- 4. Função que o robô vai executar ---
    def tarefa_do_robo():
        """
        Esta função é executada noutra thread para não
        congelar a interface gráfica principal.
        """
        try:
            # Ativa o log_box para receber os prints
            log_box.config(state=tk.NORMAL)
            
            # Chama a função principal do nosso outro ficheiro
            robo.executar_robo(
                cnpj=cnpj,
                codigo_acesso=codigo_acesso,
                placa_veiculo=placa,
                numero_solicitacao=solicitacao,
                arquivo_passageiros=ficheiro_csv
            )
        except Exception as e:
            # Imprime qualquer erro inesperado no log
            print(f"\n--- ERRO GERAL INESPERADO ---\n{e}\n")
        finally:
            # Quando o robô terminar (com sucesso ou erro),
            # reativa o botão e desativa o log
            exec_button.config(state=tk.NORMAL, text="Executar Robô")
            log_box.config(state=tk.DISABLED)
            
            # Limpa os campos de placa e solicitação para evitar cadastros acidentais
            placa_var.set("")
            solicitacao_var.set("")

    # --- 5. Iniciar a thread ---
    # O 'daemon=True' garante que a thread feche se a janela principal fechar
    threading.Thread(target=tarefa_do_robo, daemon=True).start()


def procurar_ficheiro():
    """
    Função chamada pelo botão "Procurar...".
    Abre uma janela para selecionar o ficheiro .csv.
    """
    ficheiro = filedialog.askopenfilename(filetypes=(("CSV Files", "*.csv"), ("All files", "*.*")))
    if ficheiro:
        ficheiro_var.set(ficheiro) # Atualiza o campo de texto com o caminho

# --- 1. Configuração da Janela Principal ---
root = tk.Tk()
root.title("Robô de Cadastro ANTT v1.2 (Tkinter)")
root.geometry("600x650") # Define um tamanho (largura x altura)

# --- 2. Criação do Frame Principal ---
# 'pady' e 'padx' dão um espaçamento (margem)
main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.pack(expand=True, fill="both")

# --- 3. Variáveis para guardar os dados dos campos ---
cnpj_var = tk.StringVar()
codigo_acesso_var = tk.StringVar()
placa_var = tk.StringVar()
solicitacao_var = tk.StringVar()
ficheiro_var = tk.StringVar()
lembrar_var = tk.BooleanVar()

# --- 4. Criação dos Widgets (Campos e Botões) ---

# --- Secção Credenciais ---
cred_frame = ttk.LabelFrame(main_frame, text="Credenciais da Empresa", padding="10 10")
# 'sticky="ew"' faz o widget "esticar" de leste (e) a oeste (w)
cred_frame.pack(fill="x", pady=5) 
ttk.Label(cred_frame, text="CNPJ:").pack(fill="x")
ttk.Entry(cred_frame, textvariable=cnpj_var).pack(fill="x", pady=(0, 5))
ttk.Label(cred_frame, text="Código de Acesso:").pack(fill="x")
ttk.Entry(cred_frame, textvariable=codigo_acesso_var, show="*").pack(fill="x", pady=(0, 5)) # show="*" esconde a password
ttk.Checkbutton(cred_frame, text="Lembrar credenciais", variable=lembrar_var).pack(fill="x", pady=(5, 0))

# --- Secção Viagem ---
viagem_frame = ttk.LabelFrame(main_frame, text="Dados da Viagem", padding="10 10")
viagem_frame.pack(fill="x", pady=5)
ttk.Label(viagem_frame, text="Placa do Veículo:").pack(fill="x")
ttk.Entry(viagem_frame, textvariable=placa_var).pack(fill="x", pady=(0, 5))
ttk.Label(viagem_frame, text="Nº da Solicitação:").pack(fill="x")
ttk.Entry(viagem_frame, textvariable=solicitacao_var).pack(fill="x", pady=(0, 5))

# --- Secção Ficheiro ---
file_frame = ttk.LabelFrame(main_frame, text="Ficheiro de Passageiros (.csv)", padding="10 10")
file_frame.pack(fill="x", pady=5)
# Frame interno para alinhar o campo e o botão na mesma linha
file_line_frame = ttk.Frame(file_frame)
file_line_frame.pack(fill="x")
ttk.Entry(file_line_frame, textvariable=ficheiro_var, state="readonly").pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
ttk.Button(file_line_frame, text="Procurar...", command=procurar_ficheiro).pack(side=tk.LEFT)

# --- Botão de Execução ---
exec_button = ttk.Button(main_frame, text="Executar Robô", command=iniciar_robo)
exec_button.pack(fill="x", pady=10, ipady=5) # 'ipady' dá uma altura interna ao botão

# --- Log de Execução ---
log_frame = ttk.LabelFrame(main_frame, text="Log de Execução", padding="10 10")
# 'expand=True, fill="both"' faz o log ocupar todo o espaço restante
log_frame.pack(fill="both", expand=True, pady=5) 
log_box = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED, height=15)
log_box.pack(fill="both", expand=True)

# --- 5. Redirecionar os 'prints' ---
redirector = PrintRedirector(log_box)
sys.stdout = redirector
sys.stderr = redirector # Redireciona 'prints' e erros

# --- 6. Iniciar a Aplicação ---
# Carregar configurações salvas
saved_cnpj, saved_code, saved_remember = load_config()
if saved_remember:
    cnpj_var.set(saved_cnpj)
    codigo_acesso_var.set(saved_code)
    lembrar_var.set(True)

print("Aplicação pronta. Preencha os dados e clique em 'Executar Robô'.\n")
root.mainloop() # Faz a janela "rodar"