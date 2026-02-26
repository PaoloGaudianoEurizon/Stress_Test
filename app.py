import streamlit as st
import pandas as pd
import numpy as np

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")

st.title("Stress Test Dashboard")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("ListaxMapping.xlsx", sheet_name=0)
    return df

df = load_data()

# =========================
# NORMALIZZAZIONE SHOCK
# =========================
def normalize_shock(row):
    """
    Converte tutti gli shock in una metrica comparabile:
    - pct resta pct
    - bps viene convertito in percentuale
    """
    if row["Shock_Type"] == "bps":
        return row["Shock_Value"] / 100  # 100 bps = 1%
    return row["Shock_Value"]

df["Shock_Normalized"] = df.apply(normalize_shock, axis=1)

# =========================
# FUNZIONE CALCOLO STRESS
# =========================
def calculate_stress(group):
    mean_stress = group["Shock_Normalized"].mean()
    
    if mean_stress > 0:
        direction = "🟢 Stress Positivo"
    elif mean_stress < 0:
        direction = "🔴 Stress Negativo"
    else:
        direction = "⚪ Neutro"
        
    return mean_stress, direction

# =========================
# LIVELLO 1
# =========================
st.header("Primo Livello Mapping")

level1_values = df["Level_1"].dropna().unique()

for l1 in level1_values:
    subset_l1 = df[df["Level_1"] == l1]
    mean_stress, direction = calculate_stress(subset_l1)
    
    with st.expander(f"{l1} | Stress medio: {round(mean_stress,2)}% | {direction}"):
        
        # =========================
        # LIVELLO 2
        # =========================
        level2_values = subset_l1["Level_2"].dropna().unique()
        
        for l2 in level2_values:
            subset_l2 = subset_l1[subset_l1["Level_2"] == l2]
            mean_stress_l2, direction_l2 = calculate_stress(subset_l2)
            
            with st.expander(f"↳ {l2} | {round(mean_stress_l2,2)}% | {direction_l2}"):
                
                # =========================
                # LIVELLO 3 (OPZIONALE)
                # =========================
                if "Level_3" in df.columns:
                    level3_values = subset_l2["Level_3"].dropna().unique()
                    
                    for l3 in level3_values:
                        subset_l3 = subset_l2[subset_l2["Level_3"] == l3]
                        mean_stress_l3, direction_l3 = calculate_stress(subset_l3)
                        
                        with st.expander(f"↳↳ {l3} | {round(mean_stress_l3,2)}% | {direction_l3}"):
                            
                            # =========================
                            # SCENARI FINALI
                            # =========================
                            scenarios = subset_l3[["Scenario", "Shock_Value", "Shock_Type"]]
                            st.dataframe(scenarios, use_container_width=True)
                
                else:
                    # Se non esiste Level_3 mostra direttamente scenari
                    scenarios = subset_l2[["Scenario", "Shock_Value", "Shock_Type"]]
                    st.dataframe(scenarios, use_container_width=True)
