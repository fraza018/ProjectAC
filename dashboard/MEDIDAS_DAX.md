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

## 🎨 Estrutura do Dashboard MVP Entregue (AC1)

O arquivo [`AC1.pbix`](AC1.pbix) foi estruturado com os seguintes visuais e componentes:

* **Linha Superior (Cards de KPIs em Container):**
  * Card 1: `Total Vendas Globais` (Volume de receita global acumulada)
  * Card 2: `Total de Jogos` (Quantidade de títulos catalogados)
  * Card 3: `Ticket Medio por Jogo` (Média de faturamento por jogo)

* **Quadrante Superior Esquerdo:**
  * **Gráfico de Área:** *Evolução Histórica das Vendas (1980 - 2016)* (Eixo X: `Year`, Eixo Y: `Total Vendas Globais`). Destaca a ascensão das 6ª e 7ª gerações de consoles.

* **Quadrante Superior Direito:**
  * **Gráfico de Colunas:** *Vendas Globais por Fabricante* (Eixo X: `Fabricante`, Eixo Y: `Total Vendas Globais`, com Rótulos de Dados ativos). Demonstra o domínio da Sony e Nintendo.

* **Quadrante Inferior Esquerdo:**
  * **Gráfico de Barras Horizontais:** *Vendas Globais por Gênero* (Eixo Y: `Genre` / `Genero`, Eixo X: `Total Vendas Globais`, com Rótulos de Dados ativos). Evidencia Ação e Esportes como líderes mundiais.

* **Quadrante Inferior Direito:**
  * **Gráfico de Rosca:** *Participação por Região* (Valores: `América do Norte`, `Europa`, `Japão`, `Outros`). Aponta a América do Norte como responsável por quase 50% da receita global.
