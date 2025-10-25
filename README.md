# Robô de Automação ANTT (Versão com Interface Gráfica)

Este projeto é uma aplicação de desktop que automatiza o processo de adição de passageiros a uma autorização de viagem no sistema da ANTT, utilizando uma interface gráfica simples e amigável.

Este repositório contém o código-fonte da aplicação. Para baixar a versão executável (pronta a usar), veja a secção "Como Usar".



## Funcionalidades

* **Interface Gráfica:** Não é preciso mexer em código. Todos os dados (credenciais, placa, etc.) são inseridos na janela da aplicação.
* **Seleção de Ficheiro:** Carregue qualquer ficheiro `.csv` de passageiros diretamente da sua pasta (ex: Downloads, Documentos).
* **Login Automático:** A aplicação faz o login e navega até à página correta da solicitação.
* **Cadastro em Lote:** Adiciona todos os passageiros do seu ficheiro `.csv` de uma só vez.
* **Log Integrado:** Veja o progresso do robô (quem foi adicionado, quem falhou) em tempo real, diretamente na janela da aplicação.
* **Relatório de Falhas:** No final da execução, um relatório é impresso no log, detalhando quais passageiros falharam e o porquê.

---

## 1. Como Usar (Para Utilizadores)

Esta é a forma mais fácil de usar o robô, sem precisar de instalar Python ou qualquer dependência.

1.  **Baixe o Aplicativo:**
    * Vá à secção **[Releases](https://github.com/GigaR4M/RoboANTT-GUI/releases)** (Lançamentos) deste repositório, no lado direito da página.
    * Baixe o ficheiro `.zip` (ex: `RoboANTT.zip`) da versão mais recente.

2.  **Descompacte o Ficheiro:**
    * Clique com o botão direito no ficheiro `.zip` baixado e selecione "Extrair tudo..." ou "Descompactar aqui".
    * Isto irá criar uma pasta (ex: `RoboANTT`).

3.  **Execute o Robô:**
    * Abra a pasta que acabou de descompactar.
    * Clique duas vezes no ficheiro `RoboANTT.exe`.
    * A janela da aplicação será aberta.

4.  **Preencha os Dados:**
    * Preencha todos os campos da aplicação (CNPJ, Código de Acesso, Placa, etc.).
    * Clique em "Procurar..." e selecione o seu ficheiro `passageiros.csv`.
    * Clique em "Executar Robô".

O robô irá abrir um navegador e começar o processo. Pode acompanhar o progresso na caixa de "Log de Execução" na parte inferior da janela.

---

## 2. Como Usar (Para Programadores - Executar o Código-Fonte)

Se você é um programador e quer executar ou modificar o código-fonte, siga estes passos.

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/GigaR4M/RoboANTT-GUI.git](https://github.com/GigaR4M/RoboANTT-GUI.git)
    cd SEU_REPOSITORIO
    ```

2.  **Crie um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # No Windows
    # source venv/bin/activate  # No macOS/Linux
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Instale os Navegadores do Playwright:**
    (O nosso script usa o Chromium)
    ```bash
    playwright install chromium
    ```

5.  **Execute a Aplicação:**
    ```bash
    python app.py
    ```

---

## Configuração do Ficheiro de Passageiros

A aplicação funciona com um ficheiro `.csv` que contém a lista de passageiros. Um ficheiro de exemplo (`passageiros.csv.example`) está incluído neste repositório.

O seu ficheiro `.csv` **deve** conter as seguintes colunas:

`nome,situacao,crianca_de_colo,tipo_documento,numero_documento,orgao_expedidor,ntelefone`

**Descrição das Colunas:**

| Coluna | Descrição | Valores Válidos / Exemplo |
| :--- | :--- | :--- |
| `nome` | Nome completo do passageiro. | `João da Silva` |
| `situacao` | Categoria do passageiro. | `"Brasileiro Maior"`, `"Brasileiro Adolescente"`, `"Brasileiro Criança"`, `"Estrangeiro"` |
| `crianca_de_colo`| Indica se é uma criança de colo. | `"sim"` (apenas para `Brasileiro Criança`), `"não"` ou deixar em branco. |
| `tipo_documento`| O tipo de documento, conforme o sistema. | `"CPF"`, `"Carteira de Identidade"`, `"CNH"`, `"Passaporte Estrangeiro"`, `"Certidão de Nascimento"`, etc. |
| `numero_documento`| O número do documento. | `12345678901` |
| `orgao_expedidor`| Órgão que emitiu o documento. | `Receita Federal`, `SSP/RN`, `DETRAN` |
| `ntelefone` | Número de telefone (opcional). | `84999998888` ou deixar em branco. |