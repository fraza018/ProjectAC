import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import (
    RandomForestRegressor,
    RandomForestClassifier,
    HistGradientBoostingRegressor,
    HistGradientBoostingClassifier
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve
)

# Garantir saída UTF-8 no Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Configurações de diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
CAMINHO_DADOS = BASE_DIR / "Dados" / "Tratado" / "vgsales_tratado.csv"
PASTA_MODELOS = BASE_DIR / "modelos"
PASTA_GRAFICOS_ML = BASE_DIR / "dashboard" / "graficos_ml"
PASTA_MODELOS.mkdir(parents=True, exist_ok=True)
PASTA_GRAFICOS_ML.mkdir(parents=True, exist_ok=True)

# Configurações estéticas de gráficos
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
plt.rcParams["axes.edgecolor"] = "#d0d7de"
plt.rcParams["axes.linewidth"] = 0.8


def carregar_e_preparar_dados():
    """
    Carrega o dataset tratado e aplica a engenharia de recursos para ML,
    garantindo que não haja data leakage (sem utilizar vendas regionais na predição).
    """
    print("=" * 70)
    print("1. CARREGAMENTO E ENGENHARIA DE FEATURES (ML PIPELINE)")
    print("=" * 70)
    
    df = pd.read_csv(CAMINHO_DADOS)
    print(f"Base carregada: {len(df)} registros e {len(df.columns)} colunas.")
    
    # 1. Agrupar Publishers de menor frequência (manter top 25 e agrupar o restante)
    top_publishers = df["Publisher"].value_counts().nlargest(25).index.tolist()
    df["Publisher_Agrupado"] = df["Publisher"].apply(
        lambda p: p if p in top_publishers else "Outras / Independentes"
    )
    
    # 2. Definir Alvo de Classificação: Sucesso Comercial (Hit >= 1 Milhão de cópias)
    df["Is_Hit"] = (df["Global_Sales"] >= 1.0).astype(int)
    
    # 3. Features preditivas (apenas características conhecidas antes do lançamento)
    features_categoricas = [
        "Platform",
        "Genero",
        "Fabricante",
        "Tipo_Plataforma",
        "Decada",
        "Publisher_Agrupado"
    ]
    features_numericas = ["Year"]
    
    X = df[features_categoricas + features_numericas].copy()
    y_reg = df["Global_Sales"].values
    y_clf = df["Is_Hit"].values
    
    print(f"Features preditivas selecionadas: {features_categoricas + features_numericas}")
    print(f"Distribuição do Alvo de Classificação (Hit >= 1M): {df['Is_Hit'].mean()*100:.2f}% Hits ({df['Is_Hit'].sum()} jogos)")
    
    return X, y_reg, y_clf, features_categoricas, features_numericas, top_publishers


def construir_preprocessor(features_categoricas, features_numericas):
    """
    Constrói o pré-processador Scikit-Learn com One-Hot Encoding e Scaling.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), features_categoricas),
            ("num", StandardScaler(), features_numericas)
        ]
    )
    return preprocessor


def treinar_e_avaliar_regressao(X_train, X_test, y_train, y_test, preprocessor):
    """
    Treina e compara 3 modelos de regressão para estimar Global_Sales.
    """
    print("\n" + "=" * 70)
    print("2. TREINAMENTO E AVALIAÇÃO DE MODELOS DE REGRESSÃO (VENDAS GLOBAIS)")
    print("=" * 70)
    
    modelos_reg = {
        "Ridge Regression (Baseline)": Ridge(alpha=1.0),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=100, max_depth=12, min_samples_split=10, random_state=42, n_jobs=-1
        ),
        "HistGradientBoosting Regressor": HistGradientBoostingRegressor(
            max_iter=120, max_depth=8, learning_rate=0.08, random_state=42
        )
    }
    
    resultados_reg = {}
    melhor_r2 = -float("inf")
    melhor_nome = None
    melhor_pipe = None
    
    for nome, reg in modelos_reg.items():
        pipe = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", reg)
        ])
        
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        # Vendas não podem ser negativas
        y_pred = np.clip(y_pred, 0, None)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        resultados_reg[nome] = {
            "MAE": round(float(mae), 4),
            "RMSE": round(float(rmse), 4),
            "R2": round(float(r2), 4),
            "pipe": pipe,
            "y_pred": y_pred
        }
        
        print(f"-> {nome:30} | R²: {r2:6.3f} | MAE: {mae:6.3f}M | RMSE: {rmse:6.3f}M")
        
        if r2 > melhor_r2:
            melhor_r2 = r2
            melhor_nome = nome
            melhor_pipe = pipe
            
    print(f"\n[Melhor Modelo de Regressão]: {melhor_nome} (R² = {melhor_r2:.4f})")
    return resultados_reg, melhor_nome, melhor_pipe


def treinar_e_avaliar_classificacao(X_train, X_test, y_train, y_test, preprocessor):
    """
    Treina e compara 3 modelos de classificação para prever se o jogo é um Hit (>= 1M).
    """
    print("\n" + "=" * 70)
    print("3. TREINAMENTO E AVALIAÇÃO DE MODELOS DE CLASSIFICAÇÃO (PREDIÇÃO DE HIT)")
    print("=" * 70)
    
    modelos_clf = {
        "Regressão Logística": LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=42
        ),
        "Random Forest Classifier": RandomForestClassifier(
            n_estimators=100, max_depth=12, class_weight="balanced", random_state=42, n_jobs=-1
        ),
        "HistGradientBoosting Classifier": HistGradientBoostingClassifier(
            max_iter=120, max_depth=8, learning_rate=0.08, class_weight="balanced", random_state=42
        )
    }
    
    resultados_clf = {}
    melhor_f1 = -float("inf")
    melhor_nome = None
    melhor_pipe = None
    
    for nome, clf in modelos_clf.items():
        pipe = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])
        
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        y_proba = pipe.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_proba)
        
        resultados_clf[nome] = {
            "Acuracia": round(float(acc), 4),
            "Precisao": round(float(prec), 4),
            "Recall": round(float(rec), 4),
            "F1-Score": round(float(f1), 4),
            "ROC-AUC": round(float(roc_auc), 4),
            "pipe": pipe,
            "y_pred": y_pred,
            "y_proba": y_proba
        }
        
        print(f"-> {nome:30} | F1: {f1:6.3f} | ROC-AUC: {roc_auc:6.3f} | Recall: {rec:6.3f} | Acc: {acc:6.3f}")
        
        # O F1-score balanceado é nossa métrica de ouro para dataset desbalanceado
        if f1 > melhor_f1:
            melhor_f1 = f1
            melhor_nome = nome
            melhor_pipe = pipe
            
    print(f"\n[Melhor Modelo de Classificação]: {melhor_nome} (F1-Score = {melhor_f1:.4f})")
    return resultados_clf, melhor_nome, melhor_pipe


def gerar_graficos_ml(resultados_reg, melhor_nome_reg, y_test_reg,
                      resultados_clf, melhor_nome_clf, y_test_clf,
                      X_train, preprocessor):
    """
    Gera gráficos de alta qualidade para evidenciar o desempenho dos modelos.
    """
    print("\n" + "=" * 70)
    print("4. GERANDO VISUALIZAÇÕES TÉCNICAS E GRÁFICOS DE ML")
    print("=" * 70)
    
    # -------------------------------------------------------------------------
    # Gráfico 1: Comparativo de Métricas dos Modelos de Regressão e Classificação
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    
    # Subplot Regressão (R² e MAE)
    nomes_reg = list(resultados_reg.keys())
    r2_vals = [resultados_reg[k]["R2"] for k in nomes_reg]
    mae_vals = [resultados_reg[k]["MAE"] for k in nomes_reg]
    x_pos = np.arange(len(nomes_reg))
    largura = 0.35
    
    b1 = axes[0].bar(x_pos - largura/2, r2_vals, largura, label="R² (Coef. Determinação)", color="#2b5c8f")
    b2 = axes[0].bar(x_pos + largura/2, mae_vals, largura, label="MAE (Erro Médio Absoluto - M)", color="#e26d5c")
    axes[0].set_title("Comparativo de Modelos: Regressão", fontsize=12, fontweight="bold", pad=12)
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels([n.replace(" Regressor", "").replace(" (Baseline)", "") for n in nomes_reg], fontsize=9)
    axes[0].grid(axis="y", linestyle="--", alpha=0.5)
    axes[0].legend(fontsize=9)
    
    for b in b1:
        axes[0].text(b.get_x() + b.get_width()/2, b.get_height() + 0.01, f"{b.get_height():.2f}",
                     ha="center", va="bottom", fontsize=8, fontweight="bold")
    for b in b2:
        axes[0].text(b.get_x() + b.get_width()/2, b.get_height() + 0.01, f"{b.get_height():.2f}M",
                     ha="center", va="bottom", fontsize=8, fontweight="bold")
                     
    # Subplot Classificação (F1-Score e ROC-AUC)
    nomes_clf = list(resultados_clf.keys())
    f1_vals = [resultados_clf[k]["F1-Score"] for k in nomes_clf]
    auc_vals = [resultados_clf[k]["ROC-AUC"] for k in nomes_clf]
    x_pos_clf = np.arange(len(nomes_clf))
    
    b3 = axes[1].bar(x_pos_clf - largura/2, f1_vals, largura, label="F1-Score", color="#2a9d8f")
    b4 = axes[1].bar(x_pos_clf + largura/2, auc_vals, largura, label="ROC-AUC", color="#e76f51")
    axes[1].set_title("Comparativo de Modelos: Classificador de Hits", fontsize=12, fontweight="bold", pad=12)
    axes[1].set_xticks(x_pos_clf)
    axes[1].set_xticklabels([n.replace(" Classifier", "").replace("Regressão ", "") for n in nomes_clf], fontsize=9)
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)
    axes[1].legend(fontsize=9)
    axes[1].set_ylim(0, 1.1)
    
    for b in b3:
        axes[1].text(b.get_x() + b.get_width()/2, b.get_height() + 0.02, f"{b.get_height():.2f}",
                     ha="center", va="bottom", fontsize=8, fontweight="bold")
    for b in b4:
        axes[1].text(b.get_x() + b.get_width()/2, b.get_height() + 0.02, f"{b.get_height():.2f}",
                     ha="center", va="bottom", fontsize=8, fontweight="bold")
                     
    plt.tight_layout()
    plt.savefig(PASTA_GRAFICOS_ML / "comparativo_modelos.png", bbox_inches="tight")
    plt.close()
    print("-> Salvo: dashboard/graficos_ml/comparativo_modelos.png")
    
    # -------------------------------------------------------------------------
    # Gráfico 2: Dispersão Real vs Predito (Melhor Modelo de Regressão)
    # -------------------------------------------------------------------------
    plt.figure(figsize=(8, 6), dpi=300)
    y_pred_reg = resultados_reg[melhor_nome_reg]["y_pred"]
    
    # Limitando visualização para vendas até 15M para clareza gráfica
    filtro_zoom = y_test_reg <= 15.0
    plt.scatter(y_test_reg[filtro_zoom], y_pred_reg[filtro_zoom], alpha=0.45, color="#1f77b4", edgecolors="none", s=25)
    
    # Linha diagonal de predição perfeita
    max_val = min(15.0, max(y_test_reg[filtro_zoom].max(), y_pred_reg[filtro_zoom].max()))
    plt.plot([0, max_val], [0, max_val], color="#d62728", linestyle="--", linewidth=2, label="Predição Ideal (y = x)")
    
    r2_reg = resultados_reg[melhor_nome_reg]["R2"]
    mae_reg = resultados_reg[melhor_nome_reg]["MAE"]
    plt.title(f"Aderência Preditiva: Real vs Estimado ({melhor_nome_reg})\nR² = {r2_reg:.3f} | MAE = {mae_reg:.3f}M", 
              fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Vendas Globais Reais (em Milhões de Cópias)", fontsize=11, labelpad=10)
    plt.ylabel("Vendas Globais Preditas pelo Modelo (em Milhões)", fontsize=11, labelpad=10)
    plt.legend(fontsize=10, loc="upper left")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xlim(0, max_val)
    plt.ylim(0, max_val)
    plt.tight_layout()
    plt.savefig(PASTA_GRAFICOS_ML / "real_vs_predito.png", bbox_inches="tight")
    plt.close()
    print("-> Salvo: dashboard/graficos_ml/real_vs_predito.png")
    
    # -------------------------------------------------------------------------
    # Gráfico 3: Matriz de Confusão do Classificador de Hits
    # -------------------------------------------------------------------------
    plt.figure(figsize=(7, 6), dpi=300)
    y_pred_clf = resultados_clf[melhor_nome_clf]["y_pred"]
    cm = confusion_matrix(y_test_clf, y_pred_clf)
    cm_perc = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis] * 100
    
    labels_cm = np.array([
        [f"{cm[0,0]}\n({cm_perc[0,0]:.1f}%)", f"{cm[0,1]}\n({cm_perc[0,1]:.1f}%)"],
        [f"{cm[1,0]}\n({cm_perc[1,0]:.1f}%)", f"{cm[1,1]}\n({cm_perc[1,1]:.1f}%)"]
    ])
    
    sns.heatmap(cm, annot=labels_cm, fmt="", cmap="Blues", cbar=True,
                xticklabels=["Comum (< 1M)", "Hit (>= 1M)"],
                yticklabels=["Comum (< 1M)", "Hit (>= 1M)"])
    plt.title(f"Matriz de Confusão: Preditor de Sucesso Comercial\n({melhor_nome_clf})", 
              fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Classe Predita pela IA", fontsize=11, labelpad=10)
    plt.ylabel("Classe Real no Histórico", fontsize=11, labelpad=10)
    plt.tight_layout()
    plt.savefig(PASTA_GRAFICOS_ML / "matriz_confusao.png", bbox_inches="tight")
    plt.close()
    print("-> Salvo: dashboard/graficos_ml/matriz_confusao.png")
    
    # -------------------------------------------------------------------------
    # Gráfico 4: Curva ROC do Classificador
    # -------------------------------------------------------------------------
    plt.figure(figsize=(7, 6), dpi=300)
    for nome, dados in resultados_clf.items():
        fpr, tpr, _ = roc_curve(y_test_clf, dados["y_proba"])
        plt.plot(fpr, tpr, linewidth=2, label=f"{nome} (AUC = {dados['ROC-AUC']:.3f})")
        
    plt.plot([0, 1], [0, 1], color="#888888", linestyle="--", label="Aleatório (AUC = 0.500)")
    plt.title("Curva ROC (Receiver Operating Characteristic) - AC2", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Taxa de Falsos Positivos (1 - Especificidade)", fontsize=11, labelpad=10)
    plt.ylabel("Taxa de Verdadeiros Positivos (Sensibilidade / Recall)", fontsize=11, labelpad=10)
    plt.legend(fontsize=9, loc="lower right")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(PASTA_GRAFICOS_ML / "curva_roc.png", bbox_inches="tight")
    plt.close()
    print("-> Salvo: dashboard/graficos_ml/curva_roc.png")
    
    # -------------------------------------------------------------------------
    # Gráfico 5: Importância das Features (Random Forest)
    # -------------------------------------------------------------------------
    plt.figure(figsize=(10, 6), dpi=300)
    rf_pipe = resultados_reg["Random Forest Regressor"]["pipe"]
    rf_model = rf_pipe.named_steps["regressor"]
    
    nomes_features_cat = rf_pipe.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out()
    nomes_features = list(nomes_features_cat) + ["Year"]
    importancias = rf_model.feature_importances_
    
    df_imp = pd.DataFrame({"Feature": nomes_features, "Importancia": importancias})
    # Limpar prefixos para exibição elegante
    df_imp["Feature"] = (df_imp["Feature"]
                         .str.replace("cat__", "")
                         .str.replace("Genero_", "Gênero: ")
                         .str.replace("Platform_", "Plataforma: ")
                         .str.replace("Fabricante_", "Fabricante: ")
                         .str.replace("Tipo_Plataforma_", "Tipo: ")
                         .str.replace("Publisher_Agrupado_", "Publisher: ")
                         .str.replace("Decada_", "Década: "))
    
    top_features = df_imp.nlargest(12, "Importancia").sort_values("Importancia", ascending=True)
    
    cores_imp = sns.color_palette("viridis", len(top_features))
    bars = plt.barh(top_features["Feature"], top_features["Importancia"] * 100, color=cores_imp, height=0.65)
    plt.title("Top 12 Fatores mais Determinantes no Volume de Vendas", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Importância Relativa no Modelo (%)", fontsize=11, labelpad=10)
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.3, bar.get_y() + bar.get_height()/2, f"{width:.1f}%",
                 va="center", ha="left", fontsize=9, fontweight="bold", color="#333333")
                 
    plt.xlim(0, top_features["Importancia"].max() * 100 * 1.15)
    plt.tight_layout()
    plt.savefig(PASTA_GRAFICOS_ML / "feature_importance.png", bbox_inches="tight")
    plt.close()
    print("-> Salvo: dashboard/graficos_ml/feature_importance.png")


def salvar_artefatos(melhor_pipe_reg, melhor_pipe_clf, top_publishers,
                     resultados_reg, resultados_clf):
    """
    Serializa os modelos treinados em .joblib e exporta as métricas em JSON.
    """
    print("\n" + "=" * 70)
    print("5. SERIALIZAÇÃO E SALVAMENTO DOS MODELOS TREINADOS (.joblib)")
    print("=" * 70)
    
    caminho_reg = PASTA_MODELOS / "modelo_regressao.joblib"
    caminho_clf = PASTA_MODELOS / "modelo_classificacao.joblib"
    caminho_meta = PASTA_MODELOS / "metadados_ml.json"
    
    joblib.dump(melhor_pipe_reg, caminho_reg)
    joblib.dump(melhor_pipe_clf, caminho_clf)
    
    metadados = {
        "top_publishers": top_publishers,
        "metricas_regressao": {
            k: {m: v for m, v in vals.items() if m not in ["pipe", "y_pred"]}
            for k, vals in resultados_reg.items()
        },
        "metricas_classificacao": {
            k: {m: v for m, v in vals.items() if m not in ["pipe", "y_pred", "y_proba"]}
            for k, vals in resultados_clf.items()
        }
    }
    
    with open(caminho_meta, "w", encoding="utf-8") as f:
        json.dump(metadados, f, ensure_ascii=False, indent=4)
        
    print(f"-> Modelo de Regressão salvo em: {caminho_reg}")
    print(f"-> Modelo de Classificação salvo em: {caminho_clf}")
    print(f"-> Metadados e métricas salvos em: {caminho_meta}")


def main():
    print("Iniciando Pipeline de Machine Learning Preditivo (AC2)...")
    
    X, y_reg, y_clf, features_cat, features_num, top_publishers = carregar_e_preparar_dados()
    
    # Divisão Estratificada para classificação e treino/teste consistente (80% treino / 20% teste)
    indices_train, indices_test = train_test_split(
        np.arange(len(X)),
        test_size=0.20,
        random_state=42,
        stratify=y_clf
    )
    
    X_train = X.iloc[indices_train]
    X_test = X.iloc[indices_test]
    y_train_reg = y_reg[indices_train]
    y_test_reg = y_reg[indices_test]
    y_train_clf = y_clf[indices_train]
    y_test_clf = y_clf[indices_test]
    
    print(f"Divisão dos Dados: {len(X_train)} amostras para Treino e {len(X_test)} para Teste.")
    
    preprocessor = construir_preprocessor(features_cat, features_num)
    
    # Treinar modelos
    resultados_reg, melhor_nome_reg, melhor_pipe_reg = treinar_e_avaliar_regressao(
        X_train, X_test, y_train_reg, y_test_reg, preprocessor
    )
    
    resultados_clf, melhor_nome_clf, melhor_pipe_clf = treinar_e_avaliar_classificacao(
        X_train, X_test, y_train_clf, y_test_clf, preprocessor
    )
    
    # Gerar gráficos avaliativos
    gerar_graficos_ml(
        resultados_reg, melhor_nome_reg, y_test_reg,
        resultados_clf, melhor_nome_clf, y_test_clf,
        X_train, preprocessor
    )
    
    # Salvar modelos e metadados
    salvar_artefatos(
        melhor_pipe_reg, melhor_pipe_clf, top_publishers,
        resultados_reg, resultados_clf
    )
    
    print("\n" + "=" * 70)
    print("PIPELINE DE MACHINE LEARNING CONCLUÍDO COM SUCESSO!")
    print("=" * 70)


if __name__ == "__main__":
    main()
