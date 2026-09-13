import sys
from pathlib import Path
import pandas as pd

# Garantir saída UTF-8 no terminal do Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Localizar a pasta principal do projeto
base_dir = Path(__file__).resolve().parent.parent

# Caminho do arquivo bruto
caminho_dados = base_dir / "Dados" / "Bruto" / "vgsales.csv"

# Caminho onde vamos salvar os dados tratados
pasta_tratado = base_dir / "Dados" / "Tratado"

# Criar a pasta Tratado caso ela ainda não exista
pasta_tratado.mkdir(parents=True, exist_ok=True)

# Carregar os dados
df = pd.read_csv(caminho_dados)

print("Dados carregados com sucesso!")
print(f"Quantidade de linhas: {len(df)}")
print(f"Quantidade de colunas: {len(df.columns)}")

# ==============================================================================
# 1. VERIFICAÇÃO DE TIPOS DAS COLUNAS
# ==============================================================================
print("\n" + "=" * 60)
print("1. VERIFICAÇÃO DOS TIPOS DAS COLUNAS")
print("=" * 60)

resumo_colunas = pd.DataFrame({
    "Tipo Atual": df.dtypes,
    "Não-Nulos": df.notnull().sum(),
    "Nulos": df.isnull().sum(),
    "% Nulos": (df.isnull().sum() / len(df) * 100).round(2)
})
print(resumo_colunas)

print("\nObservação sobre tipos:")
print("- 'Year' está como float64 porque o pandas converte colunas numéricas com")
print("  valores nulos (NaN) para float. Pode ser convertido para 'Int64' (inteiro com suporte a nulos).")

# ==============================================================================
# 2. VERIFICAÇÃO DE VALORES FALTANTES (NULOS / TEXTUAIS)
# ==============================================================================
print("\n" + "=" * 60)
print("2. VALORES FALTANTES E PLACEHOLDERS")
print("=" * 60)
print("Valores nulos por coluna antes do tratamento:")
print(df.isnull().sum()[df.isnull().sum() > 0])

# Preencher publishers ausentes como 'Unknown'
df["Publisher"] = df["Publisher"].fillna("Unknown")
print("\nApós preenchimento de 'Publisher' ausentes:")
print(f"Valores nulos restantes em Publisher: {df['Publisher'].isnull().sum()}")

# Checagem de placeholders comuns (ex: 'Unknown', 'N/A')
publishers_desconhecidos = (df["Publisher"] == "Unknown").sum()
print(f"Total de registros com Publisher='Unknown': {publishers_desconhecidos}")

# ==============================================================================
# 3. VERIFICAÇÃO DE VALORES INCONSISTENTES
# ==============================================================================
print("\n" + "=" * 60)
print("3. VERIFICAÇÃO DE INCONSISTÊNCIAS")
print("=" * 60)

# 3.1 Vendas negativas
colunas_vendas = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]
vendas_negativas = (df[colunas_vendas] < 0).sum()
print("A) Vendas com valores negativos:")
print(vendas_negativas)

# 3.2 Inconsistência na soma das vendas (Global_Sales vs Soma das Regiões)
soma_regional = df[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]].sum(axis=1)
diferenca_vendas = (df["Global_Sales"] - soma_regional).abs()
# Tolerância de 0.05M para desconsiderar pequenos arredondamentos da base original
divergencias_relevantes = df[diferenca_vendas > 0.05]
print(f"\nB) Vendas globais divergentes da soma regional (> 0.05M): {len(divergencias_relevantes)}")

# 3.3 Anos fora do período plausível (antes de 1980 ou futuros/anômalos)
anos_anomalos = df[(df["Year"] < 1980) | (df["Year"] > 2020)]
print(f"\nC) Jogos com anos fora da faixa esperada (1980-2020): {len(anos_anomalos)}")

# Exemplo de anomalia conhecida no dataset (jogos de Nintendo DS registrados após descontinuação)
jogos_ano_suspeito = df[df["Year"] >= 2017][["Rank", "Name", "Platform", "Year"]]
if not jogos_ano_suspeito.empty:
    print("\nJogos registrados com ano >= 2017 (possíveis anomalias de data):")
    print(jogos_ano_suspeito.to_string(index=False))

# 3.4 Registros 100% duplicados
duplicados_completos = df.duplicated().sum()
print(f"\nD) Linhas 100% duplicadas: {duplicados_completos}")

# 3.5 Duplicatas lógicas (Mesmo Jogo na Mesma Plataforma)
duplicados_chave = df[df.duplicated(subset=["Name", "Platform"], keep=False)]
print(f"\nE) Registros com mesmo Nome e Plataforma duplicados: {len(duplicados_chave)} (linhas envolvidas)")
if not duplicados_chave.empty:
    print(duplicados_chave[["Rank", "Name", "Platform", "Year", "Global_Sales"]].sort_values(by=["Name", "Platform"]).to_string(index=False))

# 3.6 Unicidade de Ranks
ranks_duplicados = df["Rank"].duplicated().sum()
print(f"\nF) Ranks duplicados: {ranks_duplicados}")

# ==============================================================================
# 4. EXECUÇÃO DA LIMPEZA E TRATAMENTO DOS DADOS
# ==============================================================================
print("\n" + "=" * 60)
print("4. EXECUTANDO A LIMPEZA E TRANSFORMAÇÃO DOS DADOS")
print("=" * 60)

linhas_iniciais = len(df)

# 4.1 Correção de anomalia conhecida de lançamento
# "Imagine: Makeup Artist" para Nintendo DS foi lançado em 2009, mas consta como 2020
filtro_anomalia = (df["Name"] == "Imagine: Makeup Artist") & (df["Platform"] == "DS") & (df["Year"] == 2020)
if filtro_anomalia.any():
    df.loc[filtro_anomalia, "Year"] = 2009
    print("- Anomalia corrigida: 'Imagine: Makeup Artist' (DS) ajustado para o ano 2009.")

# 4.2 Remoção de registros com 'Year' nulo (essencial para análises temporais)
df_tratado = df.dropna(subset=["Year"]).copy()
linhas_removidas_ano = linhas_iniciais - len(df_tratado)
print(f"- Registros sem ano removidos: {linhas_removidas_ano} ({linhas_removidas_ano / linhas_iniciais * 100:.2f}% da base).")

# 4.3 Tratamento de duplicatas de mesma plataforma e ano
# Mantém a ocorrência principal (com maior volume ou primeiro registro oficial)
duplicados_mesmo_ano = df_tratado.duplicated(subset=["Name", "Platform", "Year"], keep="first").sum()
if duplicados_mesmo_ano > 0:
    df_tratado = df_tratado.drop_duplicates(subset=["Name", "Platform", "Year"], keep="first").copy()
    print(f"- Registros duplicados na mesma plataforma/ano removidos: {duplicados_mesmo_ano}.")

# 4.4 Conversão de tipos
# Agora que não há mais valores nulos em 'Year', podemos convertê-lo para inteiro
df_tratado["Year"] = df_tratado["Year"].astype(int)
print("- Coluna 'Year' convertida com sucesso de float64 para int64 (inteiro).")

# 4.5 Arredondamento das colunas de vendas (2 casas decimais para consistência no Power BI)
df_tratado[colunas_vendas] = df_tratado[colunas_vendas].round(2)
print("- Colunas de vendas formatadas e arredondadas para 2 casas decimais.")

# ==============================================================================
# 5. ENRIQUECIMENTO DE DADOS (NOVAS COLUNAS ESTRATÉGICAS PARA O POWER BI)
# ==============================================================================
print("\n" + "=" * 60)
print("5. ENRIQUECIMENTO DE DADOS (FEATURE ENGINEERING)")
print("=" * 60)

# 5.1 Fabricante / Marca da Plataforma (Agrupa 31 plataformas em grandes empresas)
mapa_fabricantes = {
    "Wii": "Nintendo", "NES": "Nintendo", "GB": "Nintendo", "DS": "Nintendo",
    "SNES": "Nintendo", "GBA": "Nintendo", "3DS": "Nintendo", "N64": "Nintendo",
    "GC": "Nintendo", "WiiU": "Nintendo",
    "PS": "Sony", "PS2": "Sony", "PS3": "Sony", "PS4": "Sony", "PSP": "Sony", "PSV": "Sony",
    "XB": "Microsoft", "X360": "Microsoft", "XOne": "Microsoft",
    "PC": "PC",
    "GEN": "Sega", "DC": "Sega", "SAT": "Sega", "SCD": "Sega", "GG": "Sega",
    "2600": "Atari"
}
df_tratado["Fabricante"] = df_tratado["Platform"].map(mapa_fabricantes).fillna("Outros")
print("- Coluna 'Fabricante' criada (Nintendo, Sony, Microsoft, Sega, Atari, PC, Outros).")

# 5.2 Tipo de Plataforma (Console de Mesa, Portátil ou Computador)
portateis = ["DS", "GB", "GBA", "3DS", "PSP", "PSV", "WS", "GG"]
def classificar_tipo_plataforma(plataforma):
    if plataforma == "PC":
        return "Computador"
    elif plataforma in portateis:
        return "Portátil"
    else:
        return "Console de Mesa"

df_tratado["Tipo_Plataforma"] = df_tratado["Platform"].apply(classificar_tipo_plataforma)
print("- Coluna 'Tipo_Plataforma' criada (Console de Mesa, Portátil, Computador).")

# 5.3 Década de Lançamento (Excelente para filtros e linhas do tempo)
def classificar_decada(ano):
    if ano < 1990:
        return "Anos 80"
    elif ano < 2000:
        return "Anos 90"
    elif ano < 2010:
        return "Anos 2000"
    else:
        return "Anos 2010+"

df_tratado["Decada"] = df_tratado["Year"].apply(classificar_decada)
print("- Coluna 'Decada' criada (Anos 80, Anos 90, Anos 2000, Anos 2010+).")

# 5.4 Maior Mercado Regional de Cada Jogo
nomes_regioes = {
    "NA_Sales": "América do Norte",
    "EU_Sales": "Europa",
    "JP_Sales": "Japão",
    "Other_Sales": "Outros"
}
colunas_regionais = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
df_tratado["Maior_Mercado"] = df_tratado[colunas_regionais].idxmax(axis=1).map(nomes_regioes)
print("- Coluna 'Maior_Mercado' criada (indica onde cada jogo teve mais sucesso de vendas).")

# 5.5 Faixa de Sucesso Comercial
def classificar_faixa_vendas(venda_global):
    if venda_global >= 5.0:
        return "1. Super-Hit (> 5M)"
    elif venda_global >= 1.0:
        return "2. Sucesso (1M a 5M)"
    elif venda_global >= 0.1:
        return "3. Médio (100k a 1M)"
    else:
        return "4. Nicho (< 100k)"

df_tratado["Faixa_Vendas"] = df_tratado["Global_Sales"].apply(classificar_faixa_vendas)
print("- Coluna 'Faixa_Vendas' criada (Segmentação comercial: Super-Hit, Sucesso, Médio, Nicho).")

# 5.6 Tradução dos Gêneros para Português
mapa_generos = {
    "Action": "Ação",
    "Sports": "Esportes",
    "Shooter": "Tiro",
    "Role-Playing": "RPG",
    "Platform": "Plataforma",
    "Misc": "Diversos",
    "Racing": "Corrida",
    "Fighting": "Luta",
    "Simulation": "Simulação",
    "Adventure": "Aventura",
    "Puzzle": "Quebra-Cabeça",
    "Strategy": "Estratégia"
}
df_tratado["Genero"] = df_tratado["Genre"].map(mapa_generos).fillna(df_tratado["Genre"])
print("- Coluna 'Genero' criada com nomes em português (Ação, Esportes, Tiro, RPG...).")

# 5.7 Colunas de Vendas Regionais com nomes em Português
df_tratado["Vendas_Am_Norte"] = df_tratado["NA_Sales"]
df_tratado["Vendas_Europa"] = df_tratado["EU_Sales"]
df_tratado["Vendas_Japao"] = df_tratado["JP_Sales"]
df_tratado["Vendas_Outros"] = df_tratado["Other_Sales"]
print("- Colunas de vendas em português criadas (Vendas_Am_Norte, Vendas_Europa...).")

# ==============================================================================
# 6. VALIDAÇÃO FINAL DOS DADOS TRATADOS
# ==============================================================================
print("\n" + "=" * 60)
print("6. VALIDAÇÃO FINAL DOS DADOS TRATADOS")
print("=" * 60)
print(f"Total de linhas antes da limpeza: {linhas_iniciais}")
print(f"Total de linhas após a limpeza : {len(df_tratado)}")
print(f"Total de colunas agora        : {len(df_tratado.columns)} (eram 11, agora são {len(df_tratado.columns)})")
print(f"Total de dados nulos restantes: {df_tratado.isnull().sum().sum()}")
print("\nColunas e tipos finais:")
print(df_tratado.dtypes)

# ==============================================================================
# 7. SALVAR ARQUIVO TRATADO PARA O POWER BI
# ==============================================================================
print("\n" + "=" * 60)
print("7. SALVANDO ARQUIVO TRATADO")
print("=" * 60)

caminho_arquivo_tratado = pasta_tratado / "vgsales_tratado.csv"

# Salvamos com encoding 'utf-8-sig' para garantir compatibilidade perfeita
# com o Power BI e Excel no Windows, preservando acentos e caracteres especiais
df_tratado.to_csv(caminho_arquivo_tratado, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo com sucesso em:")
print(f"-> {caminho_arquivo_tratado}")
print("Base tratada, enriquecida e 100% pronta para importação no Power BI!")