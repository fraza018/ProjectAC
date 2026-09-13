# 📊 Guia de Modelagem e Medidas DAX (Power BI)

Este documento contém a documentação das regras de negócio e fórmulas DAX prontas para uso no **Power BI Desktop**, utilizando a base tratada [`vgsales_tratado.csv`](../Dados/Tratado/vgsales_tratado.csv).

---

## 🛠️ Boas Práticas de Modelagem

1. **Importação:**
   - Obter Dados -> Texto/CSV -> Selecionar `Dados/Tratado/vgsales_tratado.csv`.
   - Verificar a codificação: `65001: Unicode (UTF-8)`.
2. **Criar Tabela Dedicada de Medidas:**
   - Na guia *Página Inicial*, clique em **Inserir Dados**.
   - Nomeie a tabela como `_Medidas`.
   - Todas as medidas abaixo devem ser criadas dentro dessa tabela para manter o projeto organizado.

---

## 📐 Fórmulas DAX

### 1. Faturamento Global
```dax
Total Vendas Globais = 
SUM(vgsales_tratado[Global_Sales])
```

### 2. Vendas por Região Geográfica
```dax
Vendas NA = 
SUM(vgsales_tratado[NA_Sales])

Vendas EU = 
SUM(vgsales_tratado[EU_Sales])

Vendas JP = 
SUM(vgsales_tratado[JP_Sales])

Vendas Outros = 
SUM(vgsales_tratado[Other_Sales])
```

### 3. Percentuais de Participação de Mercado (% Share Regional)
```dax
% Vendas NA = 
DIVIDE([Vendas NA], [Total Vendas Globais], 0)

% Vendas EU = 
DIVIDE([Vendas EU], [Total Vendas Globais], 0)

% Vendas JP = 
DIVIDE([Vendas JP], [Total Vendas Globais], 0)
```
*(Formatar como Percentual com 1 casa decimal).*

### 4. Métricas de Volume e Catálogo
```dax
Total de Jogos = 
COUNTROWS(vgsales_tratado)

Ticket Medio por Titulo = 
DIVIDE([Total Vendas Globais], [Total de Jogos], 0)
```

### 5. Destaques Dinâmicos (Top Performers)
```dax
Gênero Líder = 
TOPN(
    1, 
    VALUES(vgsales_tratado[Genre]), 
    [Total Vendas Globais], 
    DESC
)

Fabricante Líder = 
TOPN(
    1, 
    VALUES(vgsales_tratado[Fabricante]), 
    [Total Vendas Globais], 
    DESC
)
```

---

## 🎨 Sugestão de Layout para o Dashboard MVP

* **Linha Superior (Cards de KPIs):**
  * Card 1: `Total Vendas Globais` (em Milhões de dólares)
  * Card 2: `Total de Jogos`
  * Card 3: `Fabricante Líder`
  * Card 4: `% Vendas NA`
* **Painel Central Esquerdo:**
  * Gráfico de Linhas/Área: `Total Vendas Globais` por `Year` ou `Decada`.
  * Gráfico de Barras: Top 10 Jogos por `Total Vendas Globais`.
* **Painel Central Direito:**
  * Gráfico de Rosca: `Distribuição Regional` (`Vendas NA`, `Vendas EU`, `Vendas JP`, `Vendas Outros`).
  * Gráfico de Barras Horizontais: `Total Vendas Globais` por `Genre`.
* **Filtros Laterais (Slicers):**
  * `Fabricante` (Nintendo, Sony, Microsoft...)
  * `Decada` (Anos 80, 90, 2000, 2010+)
  * `Tipo_Plataforma` (Console de Mesa, Portátil, Computador)
  * `Faixa_Vendas` (Super-Hit, Sucesso, Médio, Nicho)
