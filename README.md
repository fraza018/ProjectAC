# 🎮 Análise de Vendas da Indústria de Games

Projeto prático de análise de dados exploratória, tratamento e visualização de vendas de videogames ao longo das décadas.

> **Status do Projeto:** Entrega 1/3 (Fundação de Dados & Dashboard MVP)

---

## 📌 Escopo da Entrega 1
- **ETL em Python:** Tratamento, limpeza e enriquecimento do dataset original (`vgsales.csv`).
  - Tratamento de valores nulos e inconsistências de catálogo.
  - Correção de tipos de dados (`Year` convertido para inteiro).
  - *Feature Engineering*: criação de colunas estratégicas (`Fabricante`, `Tipo_Plataforma`, `Decada`, `Maior_Mercado` e `Faixa_Vendas`).
  - Exportação da base padronizada em `UTF-8 com BOM` para integração com o Power BI.
- **Estrutura do Projeto:** Organização de diretórios para reprodutibilidade e versionamento.
- **Visualização (Power BI):** Construção do dashboard inicial (MVP).

---

## 📁 Estrutura de Pastas

```text
ProjetoDeJogos/
├── Dados/
│   ├── Bruto/               # Base original de dados (vgsales.csv)
│   └── Tratado/             # Base limpa e enriquecida gerada pelo Python
├── scripts/
│   ├── analise_inicial.py   # Script de exploração inicial dos dados
│   └── tratamento_dados.py  # Pipeline de limpeza, transformação e enriquecimento
├── dashboard/               # Arquivos .pbix do Power BI
├── .gitignore               # Arquivos ignorados pelo Git
└── README.md                # Documentação do projeto
```

---

## 🚀 Como Executar (Ambiente Local)

O projeto utiliza um ambiente virtual Python para gerenciar dependências.

1. **Instalar Dependências:**
   ```bash
   pip install pandas matplotlib seaborn
   ```

2. **Executar o Script de ETL:**
   ```bash
   python scripts/tratamento_dados.py
   ```

---

## 📦 Tecnologias e Ferramentas
- **Python 3.8+**
- **Pandas** (Tratamento e manipulação de dados)
- **Power BI Desktop** (Modelagem de dados, DAX e visualizações)
