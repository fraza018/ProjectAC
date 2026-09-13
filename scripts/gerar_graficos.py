import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Garantir codificação UTF-8 no Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Configurar diretórios
base_dir = Path(__file__).resolve().parent.parent
caminho_dados = base_dir / "Dados" / "Tratado" / "vgsales_tratado.csv"
pasta_graficos = base_dir / "dashboard" / "graficos"
pasta_graficos.mkdir(parents=True, exist_ok=True)

# Configurações visuais gerais do Matplotlib/Seaborn
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

print("Carregando base de dados tratada...")
df = pd.read_csv(caminho_dados)

# ==============================================================================
# 1. TOP 10 JOGOS MAIS VENDIDOS NO MUNDO
# ==============================================================================
print("1. Gerando gráfico: Top 10 Jogos Mais Vendidos...")
plt.figure(figsize=(10, 6), dpi=300)
top10 = df.nlargest(10, "Global_Sales").sort_values("Global_Sales", ascending=True)

cores_top10 = sns.color_palette("viridis", len(top10))
bars = plt.barh(top10["Name"] + " (" + top10["Platform"] + ")", top10["Global_Sales"], color=cores_top10, height=0.65)

plt.title("Top 10 Jogos Mais Vendidos no Mundo (Histórico)", fontsize=14, fontweight="bold", pad=15)
plt.xlabel("Vendas Globais (em Milhões de Cópias)", fontsize=11, labelpad=10)
plt.grid(axis="x", linestyle="--", alpha=0.5)

# Rótulos de dados nas barras
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.8, bar.get_y() + bar.get_height()/2, f"{width:.1f}M", 
             va="center", ha="left", fontsize=9, fontweight="bold", color="#333333")

plt.xlim(0, top10["Global_Sales"].max() * 1.12)
plt.tight_layout()
plt.savefig(pasta_graficos / "top10_jogos.png", bbox_inches="tight")
plt.close()

# ==============================================================================
# 2. PARTICIPAÇÃO DE VENDAS POR FABRICANTE
# ==============================================================================
print("2. Gerando gráfico: Vendas por Fabricante...")
plt.figure(figsize=(9, 5), dpi=300)
vendas_fab = df.groupby("Fabricante")["Global_Sales"].sum().sort_values(ascending=False)

cores_fab = ["#e4000f", "#003791", "#107c10", "#0080ff", "#ff8000", "#6c757d", "#adb5bd"]
cores_plot = cores_fab[:len(vendas_fab)]

bars_fab = plt.bar(vendas_fab.index, vendas_fab.values, color=cores_plot, width=0.6)
plt.title("Volume Total de Vendas por Fabricante / Marca", fontsize=14, fontweight="bold", pad=15)
plt.ylabel("Vendas Globais (em Milhões)", fontsize=11, labelpad=10)
plt.xlabel("Fabricante", fontsize=11, labelpad=10)
plt.grid(axis="y", linestyle="--", alpha=0.5)

for bar in bars_fab:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 40, f"{height:.0f}M", 
             ha="center", va="bottom", fontsize=9, fontweight="bold", color="#333333")

plt.ylim(0, vendas_fab.max() * 1.15)
plt.tight_layout()
plt.savefig(pasta_graficos / "vendas_fabricante.png", bbox_inches="tight")
plt.close()

# ==============================================================================
# 3. DISTRIBUIÇÃO REGIONAL DE RECEITA
# ==============================================================================
print("3. Gerando gráfico: Distribuição Regional...")
plt.figure(figsize=(8, 6), dpi=300)
vendas_regionais = {
    "América do Norte": df["NA_Sales"].sum(),
    "Europa": df["EU_Sales"].sum(),
    "Japão": df["JP_Sales"].sum(),
    "Outras Regiões": df["Other_Sales"].sum()
}
labels = list(vendas_regionais.keys())
valores = list(vendas_regionais.values())
cores_regioes = ["#2b5c8f", "#418fde", "#e26d5c", "#f4a261"]

wedges, texts, autotexts = plt.pie(
    valores, 
    labels=labels, 
    autopct=lambda pct: f"{pct:.1f}%\n({pct * sum(valores) / 100:.0f}M)",
    startangle=140, 
    colors=cores_regioes,
    wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
    pctdistance=0.75
)

for autotext in autotexts:
    autotext.set_fontsize(9)
    autotext.set_fontweight("bold")

plt.title("Distribuição Global de Vendas por Região Geográfica", fontsize=13, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig(pasta_graficos / "distribuicao_regional.png", bbox_inches="tight")
plt.close()

# ==============================================================================
# 4. FATURAMENTO TOTAL POR GÊNERO DE JOGO
# ==============================================================================
print("4. Gerando gráfico: Vendas por Gênero...")
plt.figure(figsize=(10, 6), dpi=300)
coluna_gen = "Genero" if "Genero" in df.columns else "Genre"
vendas_genero = df.groupby(coluna_gen)["Global_Sales"].sum().sort_values(ascending=True)

cores_gen = sns.color_palette("mako", len(vendas_genero))
bars_gen = plt.barh(vendas_genero.index, vendas_genero.values, color=cores_gen, height=0.65)

plt.title("Vendas Globais Acumuladas por Gênero de Jogo", fontsize=14, fontweight="bold", pad=15)
plt.xlabel("Total de Vendas Globais (em Milhões)", fontsize=11, labelpad=10)
plt.grid(axis="x", linestyle="--", alpha=0.5)

for bar in bars_gen:
    width = bar.get_width()
    plt.text(width + 15, bar.get_y() + bar.get_height()/2, f"{width:.0f}M", 
             va="center", ha="left", fontsize=9, fontweight="bold", color="#333333")

plt.xlim(0, vendas_genero.max() * 1.15)
plt.tight_layout()
plt.savefig(pasta_graficos / "vendas_por_genero.png", bbox_inches="tight")
plt.close()

print(f"\nTodos os 4 gráficos foram gerados com sucesso na pasta:\n-> {pasta_graficos}")
