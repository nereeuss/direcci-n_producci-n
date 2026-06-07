import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os

# Allow imports from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from calculos import Previsionador

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Previsión de la Demanda", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stMetricValue"] { color: #1f1f1f !important; }
[data-testid="stMetricLabel"] { color: #31333F !important; }
.stMetric {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #d1d5db;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.page-header {
    text-align: center;
    padding: 35px 30px;
    background-color: #059669;
    border-radius: 20px;
    margin-bottom: 32px;
    box-shadow: 0 10px 40px rgba(6,78,59,0.30);
}
.page-header h1 { color: #fff; font-size: 2.2rem; font-weight: 800; margin: 0 0 8px 0; text-transform: uppercase; }
.page-header p  { color: #a7f3d0; font-size: 1rem; margin: 0; }

.welcome-container {
    text-align: center;
    padding: 60px;
    background-color: #f0f2f6;
    border-radius: 20px;
    border: 3px dashed #31333F;
    margin-top: 20px;
    color: #31333F;
}
.welcome-container h2 { color: #000 !important; font-weight: bold; margin-bottom: 10px; }
.welcome-container p  { color: #444 !important; font-size: 18px; }
/* Fix input legibility when forcing white backgrounds */
[data-baseweb="input"], [data-baseweb="select"], [data-baseweb="radio"] { background-color: #ffffff !important; }
[data-baseweb="input"] input, [data-baseweb="select"] span { color: #1f1f1f !important; }
/* Hide default page navigation */
[data-testid="stSidebarNav"] { display: none !important; }

/* Global Table Header Style */
[data-testid="stDataFrame"] th, [data-testid="stDataEditor"] th {
    background-color: #0066cc !important;
    color: white !important;
    font-weight: bold !important;
    border: 1px solid black !important;
}
[data-testid="stDataFrame"] td, [data-testid="stDataEditor"] td {
    border: 1px solid black !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>TEMA 4 · PREVISIÓN DE LA DEMANDA</h1>
    <p>Alisado exponencial y medias móviles</p>
</div>
""", unsafe_allow_html=True)

# ── Navigation ───────────────────────────────────────────────────────────────
with st.sidebar:
    if st.button("← MENÚ PRINCIPAL", use_container_width=True, key="nav_home"):
        st.switch_page("app.py")
    st.divider()
    st.markdown("### TEMAS")
    st.page_link("pages/1_Punto_Equilibrio.py", label="1. SISTEMAS PRODUCTIVOS")
    st.page_link("pages/2_Gestion_Stocks.py", label="2. GESTIÓN DE STOCKS")
    st.page_link("pages/4_Prevision_Demanda.py", label="4. PREVISIÓN DEMANDA")
    st.page_link("pages/5_Planificacion_Ventas.py", label="5. PLANIFICACIÓN")
    st.page_link("pages/6_MRP_MPS.py", label="6. MRP Y MPS")
    st.page_link("pages/7_Control_Produccion.py", label="7. CONTROL PRODUCCIÓN")
    st.page_link("pages/8_Lean_Manufacturing.py", label="8. LEAN MANUFACTURING")
    st.divider()

# ── Base Data ────────────────────────────────────────────────────────────────
st.markdown("### DATOS HISTÓRICOS (DEMANDA)")

default_data = pd.DataFrame({
    "Periodo (t)": [f"t={i}" for i in range(1, 13)],
    "Demanda (dt)": [120.0, 135.0, 140.0, 150.0, 165.0, 180.0, 175.0, 190.0, 205.0, 210.0, 220.0, 235.0]
})

edited_data = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Periodo (t)": st.column_config.TextColumn("Periodo (t)", disabled=True),
        "Demanda (dt)": st.column_config.NumberColumn("Demanda (dt)", min_value=0.0, format="%.1f")
    }
)

serie = edited_data["Demanda (dt)"].dropna().reset_index(drop=True)
n_total = len(serie)

if n_total == 0:
    st.warning("INTRODUCE DATOS DE DEMANDA PARA PODER REALIZAR LAS PREVISIONES.")
    st.stop()

motor = Previsionador(serie)

st.markdown("---")
st.markdown("### MODELOS DE PREVISIÓN")

default_idx = 0
if "active_ejercicio" in st.session_state:
    selected_ex = st.session_state["active_ejercicio"]
    if "ALISADO" in selected_ex:
        default_idx = 0
    elif "PONDERADA" in selected_ex:
        default_idx = 4
    elif "MÓVIL" in selected_ex:
        default_idx = 3

metodo = st.radio("SELECCIONA EL MÉTODO", 
    ["ALISADO SIMPLE", "ALISADO DOBLE", "ALISADO TRIPLE", "MEDIA MÓVIL", "MEDIA MÓVIL PONDERADA"],
    index=default_idx, horizontal=True)

def style_res(row):
    styles = []
    for col in row.index:
        if col == "t":
            styles.append("background-color: #0066cc; color: white; font-weight: bold; text-align: center;")
        else:
            styles.append("background-color: #f8fafc; color: black; text-align: center;")
    return styles

def render_results(df_res, pron_sig, pt_col, titulo):
    df_res["|e(t-i)|"] = df_res["e(t-i)"].abs()
    df_res["(e(t-i))2"] = df_res["e(t-i)"] ** 2

    m1, m2, m3 = st.columns(3)
    m1.metric("VME (Error Absoluto Medio)", f"{df_res['|e(t-i)|'].mean():.2f}")
    m2.metric("ECM (Error Cuadrático Medio)", f"{df_res['(e(t-i))2'].mean():.2f}")
    m3.metric(f"Pronóstico (T={n_total + 1})", f"{pron_sig:.2f}")

    cg1, cg2 = st.columns(2)
    with cg1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_res["t"], y=df_res["dt"], name="Real", mode="lines+markers", line=dict(color="#1f77b4", width=3)))
        if pt_col is not None:
            fig1.add_trace(go.Scatter(x=df_res["t"], y=pt_col, name="Pronóstico", line=dict(dash="dash", color="red", width=2)))
        else:
            fig1.add_hline(y=pron_sig, line_dash="dash", line_color="red", annotation_text="Pronóstico")
            
        fig1.update_layout(
            title=f"EVOLUCIÓN HISTÓRICA VS PRONÓSTICO ({titulo})", 
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
            yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
            legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5),
            margin=dict(t=80, b=120, l=10, r=10)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with cg2:
        st.dataframe(df_res.style.apply(style_res, axis=1).format(precision=2, na_rep=""), use_container_width=True, hide_index=True)


if metodo == "ALISADO SIMPLE":
    st.markdown("#### PARÁMETROS: ALISADO SIMPLE")
    alpha_1 = st.slider("Alpha (α)", 0.0, 1.0, 0.20, 0.01, key="alpha_1")
    at_col, _, pt_col = motor.alisado_simple_excel(alpha_1)
    pron_sig = at_col.iloc[-1] + alpha_1 * (serie.iloc[-1] - at_col.iloc[-1])
    
    df_res = pd.DataFrame({"t": range(1, n_total + 1), "dt": serie})
    df_res["e(t-i)"] = pt_col - df_res["dt"]
    df_res.loc[0, "e(t-i)"] = np.nan
    render_results(df_res, pron_sig, pt_col, "ALISADO SIMPLE")

elif metodo == "ALISADO DOBLE":
    st.markdown("#### PARÁMETROS: ALISADO DOBLE")
    c1, c2 = st.columns(2)
    alpha_2 = c1.slider("Alpha (α)", 0.0, 1.0, 0.20, 0.01, key="alpha_2")
    beta_2 = c2.slider("Beta (β)", 0.0, 1.0, 0.30, 0.01, key="beta_2")
    
    at_col, bt_col, pt_col = motor.alisado_doble_excel(alpha_2, beta_2)
    pron_sig = pt_col.iloc[-1]
    
    df_res = pd.DataFrame({"t": range(1, n_total + 1), "dt": serie})
    df_res["e(t-i)"] = pt_col - df_res["dt"]
    df_res.loc[0, "e(t-i)"] = np.nan
    render_results(df_res, pron_sig, pt_col, "ALISADO DOBLE")

elif metodo == "ALISADO TRIPLE":
    st.markdown("#### PARÁMETROS: ALISADO TRIPLE")
    c1, c2, c3, c4 = st.columns(4)
    alpha_3 = c1.slider("Alpha (α)", 0.0, 1.0, 0.20, 0.01, key="alpha_3")
    beta_3 = c2.slider("Beta (β)", 0.0, 1.0, 0.30, 0.01, key="beta_3")
    gamma_3 = c3.slider("Gamma (γ)", 0.0, 1.0, 0.40, 0.01, key="gamma_3")
    L_3 = c4.number_input("Ciclo (L)", 1, 52, 4, key="L_3")
    
    at_col, bt_col, ct_col, pt_col = motor.alisado_triple_excel(alpha_3, beta_3, gamma_3, L_3)
    pron_sig = pt_col.iloc[-1]
    
    df_res = pd.DataFrame({"t": range(1, n_total + 1), "dt": serie})
    df_res["e(t-i)"] = pt_col - df_res["dt"]
    df_res.loc[0, "e(t-i)"] = np.nan
    render_results(df_res, pron_sig, pt_col, "ALISADO TRIPLE")

elif metodo == "MEDIA MÓVIL":
    st.markdown("#### PARÁMETROS: MEDIA MÓVIL")
    k_4 = st.number_input("Periodos (k)", 1, n_total, min(3, n_total), key="k_4")
    
    pt_col, pron_sig = motor.media_movil_excel(k_4)
    df_res = pd.DataFrame({"t": range(1, n_total + 1), "dt": serie})
    df_res["e(t-i)"] = pt_col - df_res["dt"]
    render_results(df_res, pron_sig, pt_col, "MEDIA MÓVIL")

elif metodo == "MEDIA MÓVIL PONDERADA":
    st.markdown("#### PARÁMETROS: MEDIA MÓVIL PONDERADA")
    st.caption("Ajusta los pesos para cada periodo histórico.")
    
    df_pesos = pd.DataFrame({
        "Periodo (t)": [f"t={i+1}" for i in range(n_total)],
        "Peso (W)": [1.0 / n_total] * n_total
    })
    
    edited_pesos = st.data_editor(
        df_pesos,
        num_rows="fixed",
        use_container_width=True,
        hide_index=True,
        key="pesos_editor",
        column_config={
            "Periodo (t)": st.column_config.TextColumn("Periodo (t)", disabled=True),
            "Peso (W)": st.column_config.NumberColumn("Peso (W)", min_value=0.0, max_value=1.0, format="%.3f")
        }
    )
    
    pesos = edited_pesos["Peso (W)"].tolist()
    
    if not np.isclose(sum(pesos), 1.0, atol=0.001):
        st.warning(f"LA SUMA DE LOS PESOS ES {sum(pesos):.3f}. DEBERÍA SER 1.0")
    else:
        df_res = pd.DataFrame({"t": range(1, n_total + 1), "W(t-i)": pesos, "dt": serie})
        df_res["W(t-i) * dt"] = df_res["W(t-i)"] * df_res["dt"]
        pron_sig = df_res["W(t-i) * dt"].sum()
        
        df_res["e(t-i)"] = np.nan
        df_res.loc[df_res["W(t-i)"] > 0, "e(t-i)"] = pron_sig - df_res["dt"]
        
        pt_col = pd.Series(np.full(n_total, np.nan))
        pt_col[df_res["W(t-i)"] > 0] = pron_sig
        
        render_results(df_res, pron_sig, pt_col, "MEDIA MÓVIL PONDERADA")
