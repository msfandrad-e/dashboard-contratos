# 📊 Dashboard de Controle de Contratos

Aplicação interativa desenvolvida em Python para acompanhamento, análise e visualização de dados contratuais.

O projeto permite importar bases de dados, aplicar filtros, acompanhar indicadores e explorar informações por meio de visualizações interativas.

## 🚀 Demonstração online

**[Acessar Dashboard de Controle de Contratos](https://dashboard-contratos-jsvjuefcstgypfra9jdfvc.streamlit.app/)**

## 🎯 Objetivo do projeto

Desenvolver uma ferramenta de apoio à análise e ao acompanhamento de contratos, facilitando a identificação de informações relevantes, o monitoramento de prazos e a visualização de indicadores para auxiliar a tomada de decisões.

## ⚙️ Funcionalidades

- Importação de arquivos Excel e CSV.
- Tratamento e manipulação de dados.
- Filtros interativos para exploração das informações.
- Apresentação de indicadores de desempenho (KPIs).
- Visualizações gráficas interativas.
- Gráfico de Gantt para acompanhamento temporal dos contratos.
- Identificação de contratos vencidos.
- Exportação de dados em CSV, Excel e JSON.

## 🛠️ Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Desenvolvimento da aplicação |
| Streamlit | Interface interativa |
| Pandas | Manipulação e tratamento de dados |
| NumPy | Operações numéricas |
| Plotly | Visualização de dados |
| OpenPyXL | Manipulação de arquivos Excel |

## 📁 Estrutura do projeto

```text
dashboard-contratos/
│
├── .streamlit/
│   └── style.css
│
├── exemplos/
│   └── Base_Demonstracao.xlsx
│
├── App_controle.py
├── requirements.txt
└── README.md
```
## 📥 Base de dados para demonstração

Para facilitar a avaliação e a utilização da aplicação, disponibilizamos uma planilha de demonstração com dados fictícios e estrutura compatível com o dashboard.

**[Baixar planilha de demonstração](exemplos/Base_Demonstracao.xlsx)**

### Como utilizar

1. Baixe a planilha de demonstração.
2. Acesse a [aplicação online](https://dashboard-contratos-jsvjuefcstgypfra9jdfvc.streamlit.app/).
3. Faça upload do arquivo Excel.
4. Explore os indicadores, filtros e visualizações disponíveis.

## 💻 Como executar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/msfandrad-e/dashboard-contratos.git
```

### 2. Acesse a pasta do projeto

```bash
cd dashboard-contratos
```

### 3. Crie um ambiente virtual

```bash
python -m venv .venv
```

### 4. Ative o ambiente virtual

Windows:

```powershell
.venv\Scripts\activate
```

Linux:

```bash
source .venv/bin/activate
```

### 5. Instale as dependências

```bash
pip install -r requirements.txt
```

### 6. Execute a aplicação

```bash
streamlit run App_controle.py
```

A aplicação será disponibilizada localmente pelo Streamlit.

## 📌 Aprendizados e competências aplicadas

Este projeto permitiu aplicar conhecimentos relacionados a:

- Manipulação e transformação de dados com Python.
- Construção de indicadores e métricas de acompanhamento.
- Desenvolvimento de dashboards interativos.
- Visualização e análise de informações.
- Integração de bibliotecas para processamento de dados.
- Publicação de aplicações utilizando Streamlit Community Cloud.

## 👨‍💻 Autor

**Moisés Figueiredo**

- [GitHub](https://github.com/msfandrad-e)
- [LinkedIn](https://www.linkedin.com/in/mois%C3%A9s-figueiredo-de-andrade-387152300/)
