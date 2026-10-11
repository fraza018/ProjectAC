# 📊 Guia de Modelagem e Medidas DAX (Power BI)

Este documento contém a documentação das regras de negócio e fórmulas DAX prontas para uso no **Power BI Desktop**, utilizando a base tratada e enriquecida [`vgsales_tratado.csv`](../Dados/Tratado/vgsales_tratado.csv).

---

## 🛠️ Boas Práticas de Modelagem

1. **Importação e Atualização:**
   * Obter Dados -> Texto/CSV -> Selecionar `Dados/Tratado/vgsales_tratado.csv`.
   * Verificar a codificação: `65001: Unicode (UTF-8)`.
   * Se você já possui o arquivo `AC1.pbix` aberto, basta clicar no botão **"Atualizar" (Refresh)** na barra superior: todas as novas colunas preditivas do Machine Learning aparecerão imediatamente!
2. **Tabela Dedicada de Medidas:**
   * Na guia *Página Inicial*, clique em **Inserir Dados**.
   * Nomeie a tabela como `_Medidas`.
   * Crie as medidas abaixo dentro dessa tabela para manter a governança do projeto.

---

## 📐 Fórmulas DAX - Entrega 1 (AC1): Fundação Descritiva

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

## 🤖 Fórmulas DAX - Entrega 2 (AC2): Inteligência Preditiva & Machine Learning

As medidas abaixo utilizam as colunas calculadas pelo pipeline de Scikit-Learn exportadas em `vgsales_tratado.csv`:

### 6. Volume de Vendas Estimado pela IA
```dax
Total Vendas Previstas = 
SUM(vgsales_tratado[Vendas_Previstas])
```

### 7. Desvio Absoluto de Vendas (Real vs Modelo)
```dax
Desvio de Vendas = 
[Total Vendas Globais] - [Total Vendas Previstas]
```

### 8. Total de Jogos com Potencial de Hit (>= 1M de Cópias)
```dax
Total Jogos Potencial Hit = 
CALCULATE(
    COUNTROWS(vgsales_tratado),
    vgsales_tratado[Hit_Previsto] = "Sim"
)
```

### 9. % Taxa de Hits Preditiva do Catálogo
```dax
% Taxa Hits Previstos = 
DIVIDE([Total Jogos Potencial Hit], [Total de Jogos], 0)
```
*(Formatar como Percentual com 1 casa decimal).*

### 10. Média de Probabilidade de Hit
```dax
Probabilidade Media Hit = 
AVERAGE(vgsales_tratado[Probabilidade_Hit]) / 100
```
*(Formatar como Percentual com 1 casa decimal).*

---

## 🎨 Estrutura das Telas no Power BI Desktop

### 📄 Página 1: Diagnóstico Histórico de Mercado (AC1)
* **Linha Superior (Cards em Container):**
  * Card 1: `Total Vendas Globais` (~798 Milhões)
  * Card 2: `Total de Jogos` (~16 Mil títulos)
  * Card 3: `Ticket Medio por Jogo` (48,87 Mil cópias)
* **Visual 1 (Gráfico de Área):** Evolução Histórica das Vendas (1980 - 2016).
* **Visual 2 (Gráfico de Colunas):** Vendas Globais por Fabricante (Sony, Nintendo, Microsoft...).
* **Visual 3 (Gráfico de Barras Horizontais):** Vendas Globais por Gênero (Ação, Esportes, Tiro...).
* **Visual 4 (Gráfico de Rosca):** Participação por Região (América do Norte, Europa, Japão, Outros).

---

### 📄 Página 2: Inteligência Preditiva & Machine Learning (AC2)
Para criar no Power BI Desktop: clique no **botão `+` (Nova Página)** na barra inferior e renomeie para **`Inteligência Preditiva (AC2)`**.

* **Linha Superior (Cards Executivos de ML):**
  * **Card 1:** `Total Vendas Previstas` (Volume total modelado pelo algoritmo Ridge)
  * **Card 2:** `Total Jogos Potencial Hit` (Quantidade de títulos classificados como prováveis sucessos)
  * **Card 3:** `Probabilidade Media Hit` (Média de probabilidade de atingir 1 milhão de cópias)
  * **Card 4:** `Desvio de Vendas` (Diferença entre o histórico consolidado e a previsão)

* **Visual 1 (Gráfico de Dispersão - Aderência do Modelo):**
  * **Tipo:** Gráfico de Dispersão (Scatter Plot)
  * **Eixo X:** `Vendas_Previstas`
  * **Eixo Y:** `Global_Sales`
  * **Legenda:** `Desempenho_vs_Modelo` *(Superou Expectativas, Dentro do Esperado, Abaixo do Esperado)*
  * **Valores / Detalhes:** `Name`
  * *Permite identificar visualmente os "Sleep Hits" (jogos que superaram muito o modelo) e os títulos de desempenho padrão.*

* **Visual 2 (Gráfico de Colunas - Potencial por Ecossistema):**
  * **Tipo:** Gráfico de Colunas
  * **Eixo X:** `Fabricante`
  * **Eixo Y:** `Probabilidade Media Hit` (Média da probabilidade de Hit)
  * *Demonstra com clareza quais ecossistemas (Nintendo e Sony) oferecem a maior probabilidade de retorno comercial para desenvolvedores.*

* **Visual 3 (Gráfico de Rosca - Desempenho vs Expectativa):**
  * **Tipo:** Gráfico de Rosca
  * **Legenda:** `Desempenho_vs_Modelo`
  * **Valores:** `Total de Jogos`
  * *Mostra a proporção de jogos que superaram as expectativas ou ficaram dentro do esperado.*

* **Visual 4 (Tabela de Simulação e Detalhamento):**
  * **Tipo:** Tabela / Matriz
  * **Campos:** `Name`, `Platform`, `Genero`, `Publisher`, `Global_Sales`, `Vendas_Previstas`, `Probabilidade_Hit`, `Hit_Previsto`
  * **Segmentadores (Filtros Laterais):** Filtro por `Fabricante`, por `Genero` e por `Hit_Previsto`.
