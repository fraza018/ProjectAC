import sys
from pathlib import Path
import json
import joblib
import pandas as pd

# Garantir saída UTF-8 no Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_MODELOS = BASE_DIR / "modelos"
CAMINHO_REG = PASTA_MODELOS / "modelo_regressao.joblib"
CAMINHO_CLF = PASTA_MODELOS / "modelo_classificacao.joblib"
CAMINHO_META = PASTA_MODELOS / "metadados_ml.json"


def carregar_modelos():
    """Carrega os modelos serializados e metadados."""
    if not CAMINHO_REG.exists() or not CAMINHO_CLF.exists():
        print("Modelos não encontrados! Execute primeiro: python scripts/treinar_modelos_ml.py")
        sys.exit(1)
        
    modelo_reg = joblib.load(CAMINHO_REG)
    modelo_clf = joblib.load(CAMINHO_CLF)
    
    with open(CAMINHO_META, "r", encoding="utf-8") as f:
        metadados = json.load(f)
        
    return modelo_reg, modelo_clf, metadados


def estimar_fabricante(plataforma):
    mapa = {
        "Wii": "Nintendo", "NES": "Nintendo", "GB": "Nintendo", "DS": "Nintendo",
        "SNES": "Nintendo", "GBA": "Nintendo", "3DS": "Nintendo", "N64": "Nintendo",
        "GC": "Nintendo", "WiiU": "Nintendo", "Switch": "Nintendo",
        "PS": "Sony", "PS2": "Sony", "PS3": "Sony", "PS4": "Sony", "PS5": "Sony",
        "PSP": "Sony", "PSV": "Sony",
        "XB": "Microsoft", "X360": "Microsoft", "XOne": "Microsoft", "XSX": "Microsoft",
        "PC": "PC"
    }
    return mapa.get(plataforma, "Outros")


def estimar_tipo_plataforma(plataforma):
    portateis = ["DS", "GB", "GBA", "3DS", "PSP", "PSV", "Switch"]
    if plataforma == "PC":
        return "Computador"
    elif plataforma in portateis:
        return "Portátil"
    else:
        return "Console de Mesa"


def estimar_decada(ano):
    if ano < 1990:
        return "Anos 80"
    elif ano < 2000:
        return "Anos 90"
    elif ano < 2010:
        return "Anos 2000"
    else:
        return "Anos 2010+"


def prever_jogo(nome, plataforma, genero, publisher, ano, modelo_reg, modelo_clf, top_publishers):
    """
    Realiza a predição para um jogo individual.
    """
    fabricante = estimar_fabricante(plataforma)
    tipo_plat = estimar_tipo_plataforma(plataforma)
    decada = estimar_decada(ano)
    pub_agrupada = publisher if publisher in top_publishers else "Outras / Independentes"
    
    dados_entrada = pd.DataFrame([{
        "Platform": plataforma,
        "Genero": genero,
        "Fabricante": fabricante,
        "Tipo_Plataforma": tipo_plat,
        "Decada": decada,
        "Publisher_Agrupado": pub_agrupada,
        "Year": ano
    }])
    
    # 1. Predição de Vendas Globais (Regressão)
    vendas_pred = max(0.01, float(modelo_reg.predict(dados_entrada)[0]))
    
    # 2. Predição de Probabilidade de Hit (Classificação)
    prob_hit = float(modelo_clf.predict_proba(dados_entrada)[0, 1]) * 100
    is_hit_pred = prob_hit >= 50.0
    
    # 3. Classificação de Faixa de Vendas Estimada
    if vendas_pred >= 5.0:
        faixa = "Super-Hit (> 5M)"
        risco = "Baixo (Altíssimo Potencial Comercial)"
    elif vendas_pred >= 1.0:
        faixa = "Sucesso / Hit (1M a 5M)"
        risco = "Moderado / Seguro"
    elif vendas_pred >= 0.1:
        faixa = "Médio (100k a 1M)"
        risco = "Padrão de Mercado"
    else:
        faixa = "Nicho (< 100k)"
        risco = "Alto (Público Específico)"
        
    return {
        "Nome": nome,
        "Plataforma": plataforma,
        "Gênero": genero,
        "Publisher": publisher,
        "Ano": ano,
        "Vendas_Estimadas_M": round(vendas_pred, 2),
        "Copias_Estimadas": f"{int(vendas_pred * 1_000_000):,} cópias".replace(",", "."),
        "Chance_Hit_1M": f"{prob_hit:.1f}%",
        "Previsao_Hit": "SIM (Hit Comercial)" if is_hit_pred else "NÃO (Venda Regular/Nicho)",
        "Faixa_Estimada": faixa,
        "Nivel_Risco": risco
    }


def executar_cenarios_demonstracao(modelo_reg, modelo_clf, top_publishers):
    """Executa cenários pré-definidos para demonstração instantânea da AC2."""
    cenarios = [
        {
            "nome": "Super Mario Odyssey 2",
            "plataforma": "Wii",
            "genero": "Plataforma",
            "publisher": "Nintendo",
            "ano": 2015
        },
        {
            "nome": "FIFA Ultimate Soccer",
            "plataforma": "PS4",
            "genero": "Esportes",
            "publisher": "Electronic Arts",
            "ano": 2016
        },
        {
            "nome": "Call of Duty: Modern Warfare X",
            "plataforma": "X360",
            "genero": "Tiro",
            "publisher": "Activision",
            "ano": 2011
        },
        {
            "nome": "Chrono Souls (Indie RPG)",
            "plataforma": "PC",
            "genero": "RPG",
            "publisher": "Studio Pixel Indie",
            "ano": 2015
        }
    ]
    
    print("\n" + "=" * 80)
    print("🎮 SIMULADOR DE POTENCIAL COMERCIAL DE VIDEOGAMES (AC2 - DEMONSTRAÇÃO)")
    print("=" * 80)
    
    for c in cenarios:
        res = prever_jogo(
            c["nome"], c["plataforma"], c["genero"], c["publisher"], c["ano"],
            modelo_reg, modelo_clf, top_publishers
        )
        print(f"\n📌 Título: {res['Nome']}")
        print(f"   • Plataforma: {res['Plataforma']} | Gênero: {res['Gênero']} | Publisher: {res['Publisher']} ({res['Ano']})")
        print(f"   • Vendas Estimadas: {res['Vendas_Estimadas_M']} Milhões ({res['Copias_Estimadas']})")
        print(f"   • Probabilidade de Sucesso Comercial (>= 1M): {res['Chance_Hit_1M']} -> {res['Previsao_Hit']}")
        print(f"   • Segmentação Estimada: {res['Faixa_Estimada']}")
        print(f"   • Avaliação de Risco: {res['Nivel_Risco']}")
        print("-" * 80)


def modo_interativo(modelo_reg, modelo_clf, top_publishers):
    """Permite ao usuário inserir dados de qualquer jogo para prever."""
    print("\n" + "=" * 80)
    print("🎯 MODO INTERATIVO: DIGITE OS DADOS DO SEU JOGO")
    print("=" * 80)
    
    try:
        nome = input("Nome do Jogo (ex: Cyber Adventure): ").strip() or "Jogo Teste"
        plat = input("Plataforma (ex: PS4, X360, Wii, PC, PS3, DS): ").strip().upper() or "PS4"
        gen = input("Gênero (ex: Ação, Esportes, Tiro, RPG, Plataforma, Corrida): ").strip().capitalize() or "Ação"
        pub = input("Publisher (ex: Nintendo, Electronic Arts, Activision, Ubisoft, Indie): ").strip() or "Electronic Arts"
        ano_str = input("Ano de Lançamento (ex: 2015): ").strip()
        ano = int(ano_str) if ano_str.isdigit() else 2015
        
        res = prever_jogo(nome, plat, gen, pub, ano, modelo_reg, modelo_clf, top_publishers)
        
        print("\n" + "=" * 50)
        print("📊 RESULTADO DA PREVISÃO DO MODELO")
        print("=" * 50)
        print(f"Jogo: {res['Nome']}")
        print(f"Vendas Globais Previstas : {res['Vendas_Estimadas_M']}M de cópias ({res['Copias_Estimadas']})")
        print(f"Probabilidade de Hit (>=1M): {res['Chance_Hit_1M']}")
        print(f"Status Comercial          : {res['Previsao_Hit']}")
        print(f"Faixa Estimada            : {res['Faixa_Estimada']}")
        print(f"Classificação de Risco    : {res['Nivel_Risco']}")
        print("=" * 50)
    except Exception as e:
        print(f"Erro ao processar entrada: {e}")


def main():
    modelo_reg, modelo_clf, metadados = carregar_modelos()
    top_publishers = metadados.get("top_publishers", [])
    
    # Executa demonstração automática
    executar_cenarios_demonstracao(modelo_reg, modelo_clf, top_publishers)
    
    # Se passado argumento '--interativo', abre o prompt
    if len(sys.argv) > 1 and sys.argv[1] in ["--interativo", "-i", "interativo"]:
        modo_interativo(modelo_reg, modelo_clf, top_publishers)
    else:
        print("\n💡 Dica: Para testar um jogo personalizado pelo terminal, execute:")
        print("   python scripts/simular_previsao.py --interativo\n")


if __name__ == "__main__":
    main()
