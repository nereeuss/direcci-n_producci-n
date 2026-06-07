import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Control de Producción", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stMetricValue"] { color: #1f1f1f !important; }
[data-testid="stMetricLabel"] { color: #31333F !important; }
.stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.page-header { text-align: center; padding: 35px 30px; background-color: #6d28d9; border-radius: 20px; margin-bottom: 32px; box-shadow: 0 10px 40px rgba(76,29,149,0.30); }
.page-header h1 { color: #fff; font-size: 2.2rem; font-weight: 800; margin: 0 0 8px 0; text-transform: uppercase; }
.page-header p { color: #c4b5fd; font-size: 1rem; margin: 0; }
/* Fix input legibility when forcing white backgrounds */
[data-baseweb="input"], [data-baseweb="select"] { background-color: #ffffff !important; }
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
    <h1>TEMA 7 · CONTROL DE PRODUCCIÓN</h1>
    <p>Secuenciación de Tareas</p>
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

# ── Helper functions ─────────────────────────────────────────────────────────

def calcular_secuencia(df, regla):
    """Sort the dataframe according to the given sequencing rule."""
    df_sorted = df.copy()
    if regla == "FIFO":
        pass  # keep original order
    elif regla == "SPT":
        df_sorted = df_sorted.sort_values("Tiempo Procesamiento", ascending=True).reset_index(drop=True)
    elif regla == "EDD":
        df_sorted = df_sorted.sort_values("Fecha Entrega", ascending=True).reset_index(drop=True)
    elif regla == "LPT":
        df_sorted = df_sorted.sort_values("Tiempo Procesamiento", ascending=False).reset_index(drop=True)
    return df_sorted


def calcular_metricas(df_seq):
    """
    Given a sequenced DataFrame with columns Trabajo, Tiempo Procesamiento, Fecha Entrega,
    compute Tiempo de Flujo, Retraso, and return the result df + metrics dict.
    """
    df = df_seq.copy()
    n = len(df)

    # Flow time = cumulative sum of processing times
    df["Tiempo de Flujo"] = df["Tiempo Procesamiento"].cumsum()

    # Lateness = max(0, Flow Time - Due Date)
    df["Retraso"] = (df["Tiempo de Flujo"] - df["Fecha Entrega"]).clip(lower=0)

    # Calculate metrics
    sum_flow = df["Tiempo de Flujo"].sum()
    sum_proc = df["Tiempo Procesamiento"].sum()
    sum_retraso = df["Retraso"].sum()

    metricas = {
        "Tiempo medio finaliz (día)": round(sum_flow / n, 2),
        "Utilización (%)": round(sum_proc / sum_flow * 100, 2),
        "Promed trabajo sistema (día)": round(sum_flow / sum_proc, 2),
        "Retraso medio trabajo (día)": round(sum_retraso / n, 2),
    }

    return df, metricas


# ── Input data ───────────────────────────────────────────────────────────────

st.subheader("DATOS DE LOS TRABAJOS")
st.caption("Introduce los trabajos con su tiempo de procesamiento y fecha de entrega. Puedes añadir o eliminar filas.")

default_data = pd.DataFrame({
    "Trabajo": ["A", "B", "C", "D", "E"],
    "Tiempo Procesamiento": [6.0, 2.0, 8.0, 3.0, 9.0],
    "Fecha Entrega": [8.0, 6.0, 18.0, 15.0, 23.0],
})

df_input = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True,
    key="jobs_editor",
    column_config={
        "Trabajo": st.column_config.TextColumn("Trabajo", required=True),
        "Tiempo Procesamiento": st.column_config.NumberColumn("Tiempo Procesamiento", min_value=0.01, required=True, format="%.2f"),
        "Fecha Entrega": st.column_config.NumberColumn("Fecha Entrega", min_value=0.0, required=True, format="%.2f"),
    },
)

# ── Validation and calculation ───────────────────────────────────────────────

try:
    # Clean data
    df_clean = df_input.dropna(subset=["Trabajo", "Tiempo Procesamiento", "Fecha Entrega"]).copy()
    df_clean["Tiempo Procesamiento"] = pd.to_numeric(df_clean["Tiempo Procesamiento"], errors="coerce")
    df_clean["Fecha Entrega"] = pd.to_numeric(df_clean["Fecha Entrega"], errors="coerce")
    df_clean = df_clean.dropna().reset_index(drop=True)

    if len(df_clean) < 1:
        st.warning("INTRODUCE AL MENOS UN TRABAJO VÁLIDO.")
        st.stop()

    st.divider()

    # ── Calculate all rules ──────────────────────────────────────────────────
    reglas = ["FIFO", "SPT", "EDD", "LPT"]
    resultados = {}
    metricas_all = {}

    for regla in reglas:
        df_seq = calcular_secuencia(df_clean, regla)
        df_result, metricas = calcular_metricas(df_seq)
        resultados[regla] = df_result
        metricas_all[regla] = metricas

    # ── Tabs ─────────────────────────────────────────────────────────────────
    opciones = ["FIFO", "SPT", "EDD", "LPT", "RESUMEN COMPARATIVO"]
    default_idx = 0
    if "active_ejercicio" in st.session_state and st.session_state["active_ejercicio"] in opciones:
        default_idx = opciones.index(st.session_state["active_ejercicio"])

    modo = st.radio("SELECCIONA LA VISTA", opciones, index=default_idx, horizontal=True, label_visibility="collapsed")

    def style_res(row):
        styles = []
        for col in df_result.columns:
            if col == "Trabajo":
                styles.append("background-color: #0066cc; color: white; font-weight: bold;")
            else:
                styles.append("background-color: #f8fafc; color: black; text-align: center;")
        return styles

    if modo in reglas:
        st.subheader(f"REGLA: {modo}")

        df_result = resultados[modo]
        metricas = metricas_all[modo]

        # Description
        descripciones = {
            "FIFO": "**First In First Out** — Los trabajos se procesan en el orden en que llegaron.",
            "SPT": "**Shortest Processing Time** — Se priorizan los trabajos con menor tiempo de procesamiento.",
            "EDD": "**Earliest Due Date** — Se priorizan los trabajos con fecha de entrega más temprana.",
            "LPT": "**Longest Processing Time** — Se priorizan los trabajos con mayor tiempo de procesamiento.",
        }
        st.markdown(descripciones[modo])

        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tiempo medio finaliz (día)", f"{metricas['Tiempo medio finaliz (día)']:.2f}")
        m2.metric("Utilización (%)", f"{metricas['Utilización (%)']:.2f}%")
        m3.metric("Promed trabajo sistema (día)", f"{metricas['Promed trabajo sistema (día)']:.2f}")
        m4.metric("Retraso medio trabajo (día)", f"{metricas['Retraso medio trabajo (día)']:.2f}")

        # Table
        st.dataframe(
            df_result.style.apply(style_res, axis=1).format({
                "Tiempo Procesamiento": "{:.2f}",
                "Tiempo de Flujo": "{:.2f}",
                "Fecha Entrega": "{:.2f}",
                "Retraso": "{:.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

        # Sequence
        st.markdown("#### SECUENCIA RESULTANTE")
        secuencia_str = " ➔ ".join(df_result["Trabajo"].astype(str))
        st.info(f"**{secuencia_str}**")

    # ── Resumen tab ──────────────────────────────────────────────────────────
    elif modo == "RESUMEN COMPARATIVO":
        st.subheader("COMPARATIVA DE REGLAS DE SECUENCIACIÓN")

        # Build comparative table
        df_resumen = pd.DataFrame(metricas_all).T
        df_resumen.index.name = "Regla"
        df_resumen = df_resumen.reset_index()

        metric_cols = ["Tiempo medio finaliz (día)", "Utilización (%)", "Promed trabajo sistema (día)", "Retraso medio trabajo (día)"]

        # Calculate "Mínimos" row
        minimos = {"Regla": "Mínimos"}
        for col in metric_cols:
            minimos[col] = df_resumen[col].min()
            
        df_resumen = pd.concat([df_resumen, pd.DataFrame([minimos])], ignore_index=True)

        def highlight_excel_style(row):
            styles = []
            is_minimos_row = row["Regla"] == "Mínimos"
            for col in df_resumen.columns:
                if col == "Regla":
                    if is_minimos_row:
                        styles.append("background-color: #d9d9d9; color: #0066cc; font-weight: bold; border: 1px solid #0066cc;")
                    else:
                        styles.append("background-color: #0066cc; color: white; font-weight: bold;")
                else:
                    val = row[col]
                    min_val = minimos[col]
                    if not is_minimos_row and val == min_val:
                        styles.append("background-color: #ffcccc; color: #cc0000; font-weight: bold; text-align: center;")
                    elif is_minimos_row:
                        styles.append("background-color: #d9d9d9; color: #0066cc; font-weight: bold; text-align: center;")
                    else:
                        styles.append("background-color: #f8fafc; color: black; text-align: center;")
            return styles

        styled_df = df_resumen.style.apply(highlight_excel_style, axis=1).format({
            "Tiempo medio finaliz (día)": "{:.2f}",
            "Utilización (%)": "{:.2f}%",
            "Promed trabajo sistema (día)": "{:.2f}",
            "Retraso medio trabajo (día)": "{:.2f}",
        })

        st.markdown('''
        <style>
        .excel-like-table table { border-collapse: collapse; width: 100%; }
        .excel-like-table th { background-color: #0066cc !important; color: white !important; font-weight: bold !important; text-align: center !important; border: 1px solid white; }
        .excel-like-table td { border: 1px solid white; }
        </style>
        ''', unsafe_allow_html=True)
        
        st.markdown('<div class="excel-like-table">', unsafe_allow_html=True)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"SE HA PRODUCIDO UN ERROR: {e}")
