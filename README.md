# 🎮 Análise de Vendas da Indústria de Games

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard%20AC1-F2C811?style=flat&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![Status](https://img.shields.io/badge/Status-Entrega%201%2F3%20Conclu%C3%ADda-brightgreen?style=flat)]()

Projeto prático de **Engenharia de Dados (ETL), Análise Exploratória e Business Intelligence (BI)** sobre o histórico global de comercialização de videogames nas últimas quatro décadas.

> **Status do Projeto:** Entrega 1/3 (Fundação de Dados, Pipeline ETL & Dashboard MVP - AC1)

---

## 📌 Escopo da Entrega 1 (AC1)

- **Pipeline de ETL em Python:** Tratamento, limpeza e enriquecimento do dataset original (`vgsales.csv`).
  - Tratamento de registros nulos e duplicidades lógicas.
  - Correção de inconsistências temporais e anomalias de catálogo.
  - Conversão de tipos de dados (`Year` tipado como inteiro).
  - *Feature Engineering*: criação de colunas analíticas (`Fabricante`, `Tipo_Plataforma`, `Decada`, `Maior_Mercado` e `Faixa_Vendas`).
  - Tradução e padronização para português (`Genero`, `Vendas_Am_Norte`, `Vendas_Europa`, etc.).
  - Exportação da base estruturada em `UTF-8 com BOM` para integração nativa com o Power BI.
- **Visualizações Exploratórias:** Script automatizado (`gerar_graficos.py`) para geração dos gráficos de validação analítica.
- **Modelagem Analítica (Power BI):** Construção do dashboard MVP no arquivo [`dashboard/AC1.pbix`](dashboard/AC1.pbix) e catálogo de medidas DAX em [`dashboard/MEDIDAS_DAX.md`](dashboard/MEDIDAS_DAX.md).
- **Estrutura de Governança:** Repositório padronizado e versionado com boas práticas de engenharia de software e Conventional Commits.

---

## 🖥️ Dashboard Interativo no Power BI (`AC1.pbix`)

O relatório foi construído no **Power BI Desktop** e está salvo em [`dashboard/AC1.pbix`](dashboard/AC1.pbix). A estrutura visual é composta por:

1. **Faixa Superior de KPIs (Container Executivo):**
   * `Total Vendas Globais`: Volume total faturado no histórico da base (~798 Milhões de cópias nos dados filtrados).
   * `Total de Jogos`: Quantidade de títulos catalogados e analisados (~16 Mil jogos).
   * `Ticket Médio por Jogo`: Média de vendas alcançada por título lançado (48,87 Mil cópias).
2. **Evolução Histórica das Vendas (1980 - 2016):**
   * Gráfico de Área demonstrando o crescimento gradual nos anos 80 e 90, e o grande ápice da indústria entre 2006 e 2010 (gerações PS2, Wii, Xbox 360 e PS3).
3. **Vendas Globais por Fabricante:**
   * Gráfico de Colunas com rótulos de dados detalhando o faturamento por ecossistema (Sony e Nintendo disputando o topo, seguidas por Microsoft e PC).
4. **Vendas Globais por Gênero:**
   * Gráfico de Barras Horizontais evidenciando os gêneros de **Ação**, **Esportes** e **Tiro** como as maiores forças comerciais do setor.
5. **Participação por Região:**
   * Gráfico de Rosca com visual limpo apontando a América do Norte (~49%) e a Europa (~27%) como os maiores mercados consumidores do planeta.

---

## 📊 Prévias da Análise Exploratória

Visualizações geradas automaticamente via Python (`matplotlib` e `seaborn`):

| Top 10 Jogos Mais Vendidos | Distribuição Regional de Vendas |
| :---: | :---: |
| ![Top 10 Jogos](dashboard/graficos/top10_jogos.png) | ![Distribuição Regional](dashboard/graficos/distribuicao_regional.png) |

| Faturamento por Fabricante | Vendas por Gênero |
| :---: | :---: |
| ![Vendas por Fabricante](dashboard/graficos/vendas_fabricante.png) | ![Vendas por Gênero](dashboard/graficos/vendas_por_genero.png) |

---

## 📖 Dicionário de Dados (Base Tratada)

A base resultante do pipeline de ETL (`vgsales_tratado.csv`) conta com 21 colunas:

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| **Rank** | `int` | Posição no ranking global de vendas |
| **Name** | `str` | Título do jogo |
| **Platform** | `str` | Sigla da plataforma original (ex: PS2, X360, Wii) |
| **Year** | `int` | Ano de lançamento do jogo |
| **Genre** / **Genero** | `str` | Gênero traduzido em português (Ação, Esportes, Tiro, RPG...) |
| **Publisher** | `str` | Empresa publicadora |
| **NA_Sales** / **Vendas_Am_Norte** | `float` | Vendas na América do Norte (em milhões) |
| **EU_Sales** / **Vendas_Europa** | `float` | Vendas na Europa (em milhões) |
| **JP_Sales** / **Vendas_Japao** | `float` | Vendas no Japão (em milhões) |
| **Other_Sales** / **Vendas_Outros** | `float` | Vendas nas demais regiões do mundo (em milhões) |
| **Global_Sales** | `float` | Vendas globais totais (em milhões) |
| **Fabricante** | `str` | *Feature Criada:* Grupo/Marca da plataforma (Nintendo, Sony, Microsoft...) |
| **Tipo_Plataforma** | `str` | *Feature Criada:* Classificação (Console de Mesa, Portátil, Computador) |
| **Decada** | `str` | *Feature Criada:* Década de lançamento (Anos 80, 90, 2000, 2010+) |
| **Maior_Mercado** | `str` | *Feature Criada:* Região onde o jogo obteve maior receita |
| **Faixa_Vendas** | `str` | *Feature Criada:* Segmentação comercial (Super-Hit, Sucesso, Médio, Nicho) |

---

## 📁 Estrutura do Projeto

```text
ProjetoDeJogos/
├── Dados/
│   ├── Bruto/                  # Base original (vgsales.csv)
│   └── Tratado/                # Base limpa e enriquecida (vgsales_tratado.csv)
├── scripts/
│   ├── analise_inicial.py      # Exploração e estatísticas descritivas
│   ├── tratamento_dados.py     # Pipeline de limpeza e feature engineering (ETL)
│   └── gerar_graficos.py       # Geração automatizada de gráficos em alta resolução
├── dashboard/
│   ├── AC1.pbix                # Arquivo oficial do Dashboard no Power BI Desktop
│   ├── graficos/               # Imagens exportadas para relatórios e README
│   └── MEDIDAS_DAX.md          # Fórmulas DAX e documentação da tela do Power BI
├── requirements.txt            # Dependências do ecossistema Python
├── .gitignore                  # Regras de exclusão (.venv, caches, etc.)
└── README.md                   # Documentação oficial do projeto
```

---

## 🚀 Como Executar (Ambiente Local)

### 1. Clonar o Repositório e Preparar Ambiente
```powershell
# Ativar ambiente virtual existente
.\.venv\Scripts\Activate.ps1

# Ou criar um novo ambiente e instalar as dependências
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Executar o Pipeline de Dados (ETL)
Gera a base tratada com as traduções e novas variáveis:
```powershell
python scripts/tratamento_dados.py
```

### 3. Gerar os Gráficos da Análise Exploratória
Atualiza as imagens na pasta `dashboard/graficos/`:
```powershell
python scripts/gerar_graficos.py
```

### 4. Abrir o Dashboard no Power BI
Abra o arquivo [`dashboard/AC1.pbix`](dashboard/AC1.pbix) no **Power BI Desktop** para interagir com o relatório.
