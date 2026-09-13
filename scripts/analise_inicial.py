import sys
from pathlib import Path
import pandas as pd

# Garantir saída UTF-8 no terminal do Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# 1. Localizar e carregar os dados
base_dir = Path(__file__).resolve().parent.parent
caminho_dados = base_dir / "Dados" / "Bruto" / "vgsales.csv"

print(f"Carregando dados de: {caminho_dados}")
df = pd.read_csv(caminho_dados)

# 2. Dimensões e Primeiras Linhas
print("\n" + "=" * 50)
print("VISÃO GERAL DO DATASET")
print("=" * 50)
print(f"Total de linhas e colunas: {df.shape}")
print("\nPrimeiras 5 linhas:")
print(df.head())

# 3. Informações e Tipos de Dados
print("\n" + "=" * 50)
print("INFORMAÇÕES E TIPOS DE COLUNAS")
print("=" * 50)
df.info()

# 4. Dados Nulos / Faltantes
print("\n" + "=" * 50)
print("VALORES FALTANTES POR COLUNA")
print("=" * 50)
valores_nulos = df.isnull().sum()
print(valores_nulos[valores_nulos > 0])

# 5. Estatísticas Numéricas
print("\n" + "=" * 50)
print("ESTATÍSTICAS DESCRITIVAS DAS VENDAS (em milhões)")
print("=" * 50)
colunas_vendas = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]
print(df[colunas_vendas].describe())

# 6. Top 10 Jogos Mais Vendidos no Mundo
print("\n" + "=" * 50)
print("TOP 10 JOGOS MAIS VENDIDOS NO MUNDO")
print("=" * 50)
top_10 = df[["Rank", "Name", "Platform", "Year", "Global_Sales"]].head(10)
print(top_10.to_string(index=False))

# 7. Vendas Totais por Gênero
print("\n" + "=" * 50)
print("VENDAS GLOBAIS POR GÊNERO")
print("=" * 50)
vendas_genero = (
    df.groupby("Genre")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
)
print(vendas_genero)

# 8. Vendas Totais por Plataforma (Top 5)
print("\n" + "=" * 50)
print("TOP 5 PLATAFORMAS COM MAIOR VOLUME DE VENDAS")
print("=" * 50)
top_plataformas = (
    df.groupby("Platform")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
print(top_plataformas)
