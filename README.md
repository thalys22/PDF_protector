### 1. Visão Geral

A aplicação recebe um arquivo PDF via upload e insere uma marca d'água personalizada (como um CPF) em todas as páginas do documento. Ela expõe uma interface web construída em FastAPI/Flask e realiza o processamento em background. Inclui:

-   Upload seguro de arquivos PDF.
    
-   Formulário para inserção do CPF, escolha de posição (Top Left, Top Right, Bottom Left, Bottom Right) e seleção de cor.
    
-   Processamento do PDF adicionando o texto via canvas (ReportLab) e mesclando com o arquivo original (PyPDF2).
    
-   Retorno automático do novo arquivo modificado para download do usuário.
    

**Autor:** Thalys dos Santos

**Versão:** 1.0.0

### 2. Arquitetura (Camadas)

-   **Interface (App):** Flask Web UI (`app.py`, `templates/`, `static/`) responsável por renderizar o formulário e gerenciar requisições GET/POST.
    
-   **Form/Validation Layer:** Uso do WTForms para garantir que dados como CPF, Posição e Cor sejam validados antes do processamento.
    
-   **Application/Service:** Lógica de manipulação de PDF encapsulada em `pdf_modifier.py`.
    
-   **Infrastructure:** Persistência temporária do arquivo no diretório estipulado em `UPLOAD_FOLDER` e biblioteca `PyPDF2` + `reportlab` para I/O e desenho vetorial no PDF.
    

**Pipeline de Dados**

1.  Usuário preenche formulário (CPF, posição, cor) e anexa arquivo PDF.
    
2.  Arquivo é validado (via `secure_filename`) e salvo temporariamente em `./uploads/`.
    
3.  O sistema cria um PDF em memória (BytesIO) contendo apenas a marca d'água posicionada na coordenada e cor corretas.
    
4.  O sistema faz o merge página por página do arquivo original com o PDF da marca d'água em memória.
    
5.  O novo arquivo substitui o temporário e é enviado de volta ao usuário como anexo (`as_attachment=True`).
    

### 3. Estrutura do Repositório e Arquitetura

O projeto adota uma estrutura modular simples baseada no padrão MVC (Model-View-Controller) simplificado, garantindo:

-   **Independência de lógica de negócio:** A manipulação do PDF está desacoplada das rotas da web.
    
-   **Segurança no manuseio de arquivos:** Os arquivos são tratados temporariamente e verificados antes de interagir com o File System.
    


```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERFACE LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          Flask (app.py)                                  │   │
│  │  • upload_file() (Rota Principal /)                      │   │
│  │  • CPFInputForm (WTForms)                                │   │
│  │  • templates/index.html (Visão HTML)                     │   │
│  │  • static/styles.css (Estilização)                       │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└───────────────────────┼─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │       Processamento de PDF (pdf_modifier.py)             │   │
│  │  • modify_pdf()                                          │   │
│  │  • Geração de Canvas (ReportLab)                         │   │
│  │  • Merge de Páginas (PyPDF2)                             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

```

**Estrutura de Diretórios Detalhada**


```
pdf_protector/
│
├── app.py                    # Inicialização do servidor e rotas Flask
├── pdf_modifier.py           # Core do processamento de arquivos PDF
├── requirements.txt          # Dependências do projeto
│
├── static/                   # Arquivos estáticos
│   └── styles.css            # Estilização da página
│
├── templates/                # Templates HTML
│   └── index.html            # Interface principal do usuário
│
├── uploads/                  # Diretório temporário de processamento
└── .gitignore                # Regras de exclusão do Git

```

### 4. Instalação

Pré-requisitos: Python 3.10+ instalado.

Bash

```
# Clone o repositório e acesse a pasta
# Instale as dependências
pip install -r requirements.txt

```

### 5. Configuração

As configurações base da aplicação estão definidas diretamente no `app.py`. Certifique-se de que a pasta `./uploads/` exista na raiz do projeto (ou será criada no fluxo, dependendo da permissão do S.O.).

-   `SECRET_KEY`: Chave para uso de seções e Flash Messages.
    
-   `UPLOAD_FOLDER`: Diretório de manipulação de arquivos (padrão: `./uploads/`).
    

### 6. Execução Local

Iniciar a aplicação localmente:

Bash

```
python app.py
# ou
flask run

```

Acesso via navegador: `http://127.0.0.1:5000/`

### 7. Processamento de PDF (Motor Principal)

Executado via `pdf_modifier.py`.

-   A função `modify_pdf(filename, cpf, position, color, upload_folder)` é o core.
    
-   Gera um documento fantasma em memória (`BytesIO`) do tamanho A4.
    
-   Itera sobre todas as páginas do PDF enviado, chamando `page.merge_page(new_pdf.pages[0])` para sobrepor a marca d'água no documento original.
    

### 8. Sistema de Coordenadas e Cores

O `pdf_modifier` traduz a seleção de UI para coordenadas numéricas do ReportLab:

-   `top-left`: x = 500, y = 800
    
-   `top-right`: x = 500, y = 800
    
-   `bottom-left`: x = 50, y = 50
    
-   `bottom-right`: x = 500, y = 50
    
    As cores são enviadas nativamente do input HTML (`<input type="color">`) e inseridas no canvas via `can.setFillColor(color)`.
    

### 9. Endpoints Principais

**Endpoints**


`/` GET - Renderiza a página principal (formulário HTML).

`/` POST - Recebe o `multipart/form-data`, salva o arquivo, insere o CPF e devolve o PDF baixável.

### 10. Validação de Dados (WTForms)

Os dados submetidos são tratados rigorosamente pela classe `CPFInputForm`:

-   `cpf`: Campo de texto obrigatório (`DataRequired`).
    
-   `position`: Campo de múltipla escolha.
    
-   `color`: Cor hexadecimal fornecida pelo seletor de paleta do HTML5.
    
-   Arquivo (File): Validado via `secure_filename` do Werkzeug para evitar Path Traversal.
    

### 11. Exemplos de Uso (Interface)

O uso principal é através da UI web localizada em `index.html`.

1.  Insira o CPF (ex: `123.456.789-00`).
    
2.  Escolha "Top Left".
    
3.  Clique na amostra de cor e selecione "Vermelho".
    
4.  Faça upload do arquivo `documento.pdf`.
    
5.  Clique em "Submit". O arquivo processado será baixado automaticamente no seu navegador.
    

### 12. Geração de Marca d'Água (ReportLab)

O aplicativo não altera o texto nativo do PDF para evitar quebra de layout. Em vez disso:

1.  Instancia um objeto `canvas.Canvas`.
    
2.  Define a fonte fixa como `Helvetica`, tamanho 10.
    
3.  Desenha a string do CPF usando `can.drawString(x, y, cpf)`.
    

### 13. Segurança de Arquivos Temporários

-   Os arquivos são validados com `secure_filename`.
    
-   São escritos e sobrescritos utilizando as tags `rb` (Read Binary) e `wb` (Write Binary).
    
-   _Nota:_ Para uso em produção, recomenda-se implementar uma rotina de exclusão ou limpeza automática da pasta `uploads/`.
    

### 14. Feedback ao Usuário (Observabilidade UI)

A interface se comunica com o usuário utilizando o sistema de `flash_messages` nativo do Flask (Jinja2 `get_flashed_messages()`). Se o usuário:

-   Não incluir um arquivo: `"Arquivo não incluido"`.
    
-   Enviar campo vazio: `"Arquivo não selecionado"`.
    
-   Ocorrer erro na conversão: `"Erro no envio do arquivo"`.
    

### 15. Tecnologias

-   **Flask & Uvicorn/Werkzeug:** Servidor Web e roteamento HTTP.
    
-   **PyPDF2:** Leitura, gravação e merge de páginas de PDFs preexistentes.
    
-   **ReportLab:** Geração programática de elementos visuais (Canvas, Cores, Fontes) em arquivos PDF.
    
-   **Flask-WTF & WTForms:** Estruturação segura de formulários web.
    
-   **HTML5/CSS3:** Renderização visual e estilização na tela (Jinja2).
    

### 16. Scripts Úteis


**Função**

`app.py`

Execução principal do servidor, instanciamento de rotas e configurações do Flask.

`pdf_modifier.py`

Função autônoma reutilizável que aplica a regra de negócio para a marca d'água no PDF.

### 17. Deploy e Infraestrutura

A aplicação é modular e pode ser conteinerizada facilmente em Docker. Para implantação em plataformas como Heroku ou Render, utiliza-se a porta `5000` (ou a `PORT` injetada via variável de ambiente). Recomenda-se a adoção de um WSGI Server escalável, como o Gunicorn, para o ambiente de produção.

### 18. Créditos

Projeto desenvolvido e idealizado por Thalys dos Santos.
