# 🎮 Projeto de Análise de Jogos (Video Game Sales)

Este projeto realiza a análise exploratória e o tratamento de dados sobre o histórico de vendas de jogos de videogame no mundo, utilizando a base de dados **vgsales**.

---

## 📁 Estrutura do Projeto

```plaintext
ProjetoDeJogos/
├── Dados/
│   ├── Bruto/         # Base de dados original (vgsales.csv)
│   └── Tratado/       # Dados limpos e tratados (vgsales_tratado.csv)
├── scripts/
│   ├── analise_inicial.py    # Script de exploração inicial dos dados
│   └── tratamento_dados.py   # Script de limpeza, enriquecimento e tratamento
├── dashboard/         # Visualizações e dashboards (em desenvolvimento)
├── .gitignore         # Arquivos ignorados pelo Git (.venv, caches, etc.)
└── README.md          # Documentação do projeto
```

---

## 🚀 Como Executar

### 1. Criar e Ativar Ambiente Virtual

No terminal (PowerShell no Windows):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar Dependências

```powershell
pip install pandas
```

### 3. Executar os Scripts

- **Análise Inicial:**
  ```powershell
  python scripts/analise_inicial.py
  ```

- **Tratamento de Dados:**
  ```powershell
  python scripts/tratamento_dados.py
  ```
