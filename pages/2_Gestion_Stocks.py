import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Gestión de Stocks – Dirección de Producción",
    layout="wide",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.page-header { text-align: center; padding: 35px 30px; background-color: #b45309; border-radius: 20px; margin-bottom: 32px; box-shadow: 0 10px 40px rgba(0,0,0,0.25); }
.page-header h1 { color: #fff !important; font-size: 2.2rem; font-weight: 800; margin: 0 0 8px 0; text-transform: uppercase; }
.page-header p { color: #fde68a !important; font-size: 1rem; margin: 0; }
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
    <h1>TEMA 2 · GESTIÓN DE STOCKS</h1>
    <p>Modelos deterministas (EOQ) y clasificación de inventarios (ABC)</p>
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

default_index = 0
if "active_ejercicio" in st.session_state:
    if "ABC" in st.session_state["active_ejercicio"]:
        default_index = 1

modo = st.selectbox(
    "SELECCIONA EL TIPO DE MODELO",
    ["2.1 MODELO EOQ", "2.2 MODELO ABC"],
    index=default_index,
    key="stocks_modo",
)

# ═══════════════════════════════════════════════════════════════════════════════
# 2.1  MODELO EOQ
# ═══════════════════════════════════════════════════════════════════════════════
if modo.startswith("2.1"):
    st.markdown("---")
    st.subheader("2.1 MODELO EOQ (RESOLUCIÓN)")

    # Tablas de Resultados y Entradas
    c1, c2, c3 = st.columns([1.2, 1.2, 1.2])
    
    with c1:
        st.markdown("**1. PARÁMETROS INICIALES (EDITABLES)**")
        default_eoq = pd.DataFrame([
            {"Variable": "Demanda (D)", "Valor": 450.0, "Unidad": "ud/año"},
            {"Variable": "Precio (p)", "Valor": 4000.0, "Unidad": "um/ud"},
            {"Variable": "Coste emisión (Cp)", "Valor": 20000.0, "Unidad": "um/ord"},
            {"Variable": "Coste mant. (Cm)", "Valor": 800.0, "Unidad": "um/ud-año"},
            {"Variable": "Plazo reaprov (PRsem)", "Valor": 2.0, "Unidad": "sem/ord"},
            {"Variable": "Stock seguridad (SS)", "Valor": 50.0, "Unidad": "ud/ord"},
            {"Variable": "Equivalente Semanal", "Valor": 50.0, "Unidad": "sem/año"},
            {"Variable": "Equivalente diario", "Valor": 365.0, "Unidad": "dia/año"},
        ])
        edited_eoq = st.data_editor(
            default_eoq,
            num_rows="fixed",
            hide_index=True,
            use_container_width=True,
            key="eoq_editor",
            column_config={
                "Variable": st.column_config.TextColumn(disabled=True, width="medium"),
                "Unidad": st.column_config.TextColumn(disabled=True),
                "Valor": st.column_config.NumberColumn(format="%.2f")
            }
        )
        
        # Extraer variables
        val = dict(zip(edited_eoq["Variable"], edited_eoq["Valor"]))
        D = val["Demanda (D)"]
        p = val["Precio (p)"]
        Cp = val["Coste emisión (Cp)"]
        Cm = val["Coste mant. (Cm)"]
        PRsem = val["Plazo reaprov (PRsem)"]
        SS = val["Stock seguridad (SS)"]
        eq_sem = val["Equivalente Semanal"]
        eq_dia = val["Equivalente diario"]

    # Validación
    if Cm <= 0 or D <= 0:
        st.warning("EL COSTE DE MANTENIMIENTO (Cm) Y LA DEMANDA (D) DEBEN SER MAYORES A CERO.")
        st.stop()

    PRdia = (PRsem / eq_sem) * eq_dia if eq_sem > 0 else 0

    # Cálculos
    q_star = np.sqrt(2 * D * Cp / Cm)
    ct_star = p * D + np.sqrt(2 * D * Cp * Cm)
    cu_star = ct_star / D
    
    t_star = q_star / D
    i_star = 1 / t_star if t_star > 0 else 0
    
    pr_ano = PRsem / eq_sem if eq_sem > 0 else 0
    pp = pr_ano * D + SS
    sm = q_star + SS
    t_sem = t_star * eq_sem
    
    def style_res(row):
        styles = []
        for col in default_eoq.columns:
            if col == "Variable":
                styles.append("background-color: #0066cc; color: white; font-weight: bold;")
            else:
                styles.append("background-color: #f8fafc; color: black; text-align: center;")
        return styles

    with c2:
        st.markdown("**2. LOTE Y COSTES ÓPTIMOS**")
        df_opt = pd.DataFrame([
            {"Variable": "Valor óptimo tamaño lote (Q*)", "Valor": f"{q_star:,.1f}", "Unidad": "ud/ord"},
            {"Variable": "Coste total óptimo (CT*)", "Valor": f"{ct_star:,.0f}", "Unidad": "um/año"},
            {"Variable": "Coste unitario óptimo (CU*)", "Valor": f"{cu_star:,.1f}", "Unidad": "um/ud"},
        ])
        st.dataframe(df_opt.style.apply(style_res, axis=1).hide(axis="index"), use_container_width=True)
        
        st.markdown("**3. TIEMPOS ÓPTIMOS**")
        df_tiempos = pd.DataFrame([
            {"Variable": "Tiempo óptimo (T*)", "Valor": f"{t_star:,.1f}", "Unidad": "año/ord"},
            {"Variable": "Inversa tiempo óptimo (I*)", "Valor": f"{i_star:,.0f}", "Unidad": "ord/año"},
        ])
        st.dataframe(df_tiempos.style.apply(style_res, axis=1).hide(axis="index"), use_container_width=True)

    with c3:
        st.markdown("**4. PUNTOS DE PEDIDO Y STOCK**")
        df_stock = pd.DataFrame([
            {"Variable": "Plazo reaprov anual (PRaño)", "Valor": f"{pr_ano:,.2f}", "Unidad": "año/ord"},
            {"Variable": "Punto de pedido (PP)", "Valor": f"{pp:,.1f}", "Unidad": "ud/ord"},
            {"Variable": "Stock máximo (SM)", "Valor": f"{sm:,.1f}", "Unidad": "ud/ord"},
            {"Variable": "Tiempo óptimo semanal (T*sem)", "Valor": f"{t_sem:,.2f}", "Unidad": "sem/ord"},
        ])
        st.dataframe(df_stock.style.apply(style_res, axis=1).hide(axis="index"), use_container_width=True)
        
        # Fórmulas decorativas
        st.info("Q* = √(2·D·Cp/Cm)  |  CT* = p·D + √(2·D·Cp·Cm)  |  T* = Q*/D")

    # Gráficos
    st.markdown("### REPRESENTACIONES GRÁFICAS")
    cg1, cg2 = st.columns(2)
    
    with cg1:
        # Evolución temporal (diente de sierra)
        # Trazar 4 ciclos completos
        ciclos = 4
        x_puntos = []
        y_puntos = []
        for i in range(ciclos):
            x_puntos.extend([i * t_sem, i * t_sem, (i+1) * t_sem])
            y_puntos.extend([SS, sm, SS])
            
        fig1 = go.Figure()
        # Línea del stock de seguridad (naranja horizontal)
        fig1.add_trace(go.Scatter(x=[0, ciclos * t_sem], y=[SS, SS], mode="lines", name="Stock Seguridad", line=dict(color="#f97316", width=2)))
        # Línea de inventario (azul sierra)
        fig1.add_trace(go.Scatter(x=x_puntos, y=y_puntos, mode="lines", name="Nivel Stock", line=dict(color="#3b82f6", width=2)))
        
        fig1.update_layout(
            title="EVOLUCIÓN TEMPORAL EOQ",
            xaxis_title="TIEMPO (SEMANAS)",
            yaxis_title="STOCK (UD)",
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
            yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
            height=350,
            showlegend=False,
            margin=dict(t=80, b=100, l=10, r=10)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with cg2:
        # Costes
        q_range = np.linspace(max(10, q_star * 0.2), q_star * 2.5, 100)
        coste_mant = (q_range / 2) * Cm
        coste_emi = (D / q_range) * Cp
        coste_total_gestion = coste_mant + coste_emi # Sin incluir p*D para que el mínimo se vea claro
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=q_range, y=coste_emi, mode="lines", name="Coste Emisión", line=dict(color="#3b82f6", width=2)))
        fig2.add_trace(go.Scatter(x=q_range, y=coste_mant, mode="lines", name="Coste Mantenimiento", line=dict(color="#f97316", width=2)))
        fig2.add_trace(go.Scatter(x=q_range, y=coste_total_gestion, mode="lines", name="Coste Gestión (Total)", line=dict(color="#94a3b8", width=3)))
        
        # Marcar mínimo
        fig2.add_trace(go.Scatter(
            x=[q_star], y=[np.sqrt(2 * D * Cp * Cm)], 
            mode="markers", marker=dict(size=10, color="red"), name="Q* Óptimo"
        ))

        fig2.update_layout(
            title="CURVAS DE COSTES EOQ (GESTIÓN)",
            xaxis_title="TAMAÑO DE LOTE (Q)",
            yaxis_title="COSTE ANUAL",
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
            yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.4, xanchor="center", x=0.5),
            margin=dict(t=80, b=120, l=10, r=10)
        )
        st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 2.2  MODELO ABC
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown("---")
    st.subheader("2.2 MODELO ABC")
    
    st.markdown("### DATOS DE INVENTARIO (ENTRADA)")
    st.caption("Introduce o modifica los productos (demanda y coste unitario).")
    
    default_abc = pd.DataFrame({
        "Código": ["A201", "A202", "A203", "A204", "A205", "A206", "A207", "A208", "A209", "A210", "A211", "A212", "A213", "A214"],
        "Producto (ud)": [200, 1100, 200, 100, 80, 40, 700, 500, 400, 300, 60, 600, 150, 120],
        "Coste unitario (€/ud)": [140.0, 8.0, 65.0, 20.0, 75.0, 1800.0, 1.0, 85.0, 6.0, 8.0, 58.0, 2.0, 70.0, 5.0]
    })

    edited_abc = st.data_editor(
        default_abc,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="abc_editor",
        column_config={
            "Código": st.column_config.TextColumn("Código"),
            "Producto (ud)": st.column_config.NumberColumn("Producto (ud)", min_value=1, step=1),
            "Coste unitario (€/ud)": st.column_config.NumberColumn("Coste unitario (€/ud)", min_value=0.0, format="%.2f"),
        }
    )
    
    if edited_abc.empty or edited_abc["Producto (ud)"].sum() == 0:
        st.warning("INTRODUCE DATOS VÁLIDOS PARA PROCESAR.")
        st.stop()

    # Cálculos
    df = edited_abc.copy()
    df["Coste (€)"] = df["Producto (ud)"] * df["Coste unitario (€/ud)"]
    
    # Ordenar por Coste de mayor a menor
    df = df.sort_values("Coste (€)", ascending=False).reset_index(drop=True)
    
    tot_coste = df["Coste (€)"].sum()
    tot_prod = df["Producto (ud)"].sum()
    
    df["Porcentaje valor (%)"] = df["Coste (€)"] / tot_coste
    df["Porcentaje producto sobre inventario (%)"] = df["Producto (ud)"] / tot_prod
    
    df["Porcentaje inventario acumulado (%)"] = df["Porcentaje producto sobre inventario (%)"].cumsum()
    df["Porcentaje valor acumulado (%)"] = df["Porcentaje valor (%)"].cumsum()
    
    # Clasificación exacta de la captura (A <= 80% del VALOR, B <= 95%, C > 95%)
    def classify_abc(val_acum):
        if val_acum <= 0.80:
            return "A"
        elif val_acum <= 0.95:
            return "B"
        else:
            return "C"
            
    df["Tipo producto"] = df["Porcentaje valor acumulado (%)"].apply(classify_abc)
    
    # Agregar la fila de Totales
    df_res = df.copy()
    
    # Acortar los nombres para que la tabla sea más pequeña
    df_res = df_res.rename(columns={
        "Porcentaje valor (%)": "% Valor",
        "Porcentaje producto sobre inventario (%)": "% Prod s/ Inv",
        "Porcentaje inventario acumulado (%)": "% Inv Acumulado",
        "Porcentaje valor acumulado (%)": "% Valor Acumulado"
    })
    
    df_res.loc["TOTAL"] = {
        "Código": "TOTAL",
        "Producto (ud)": tot_prod,
        "Coste unitario (€/ud)": np.nan,
        "Coste (€)": tot_coste,
        "% Valor": 1.0,
        "% Prod s/ Inv": 1.0,
        "% Inv Acumulado": np.nan,
        "% Valor Acumulado": np.nan,
        "Tipo producto": ""
    }

    st.markdown("### RESOLUCIÓN ABC")

    def style_abc(row):
        styles = ['background-color: #f8fafc; color: black;'] * len(row)
        
        # Fila TOTAL
        if row.name == "TOTAL":
            return ['background-color: #d9d9d9; font-weight: bold; color: #000000; border-top: 2px solid #0066cc;' if pd.notna(v) else 'background-color: #d9d9d9; border-top: 2px solid #0066cc;' for v in row]
            
        # Color en la celda final
        tipo_col_idx = df_res.columns.get_loc("Tipo producto")
        if row["Tipo producto"] == "A":
            styles[tipo_col_idx] = 'background-color: #ef4444; color: white; font-weight: bold; text-align: center' # Rojo
        elif row["Tipo producto"] == "B":
            styles[tipo_col_idx] = 'background-color: #eab308; color: black; font-weight: bold; text-align: center' # Amarillo
        elif row["Tipo producto"] == "C":
            styles[tipo_col_idx] = 'background-color: #84cc16; color: black; font-weight: bold; text-align: center' # Verde (Apple Green)
            
        return styles

    st.dataframe(
        df_res.style.format({
            "Producto (ud)": "{:,.0f}",
            "Coste unitario (€/ud)": "{:,.2f}",
            "Coste (€)": "{:,.2f}",
            "% Valor": "{:.2%}",
            "% Prod s/ Inv": "{:.2%}",
            "% Inv Acumulado": "{:.2%}",
            "% Valor Acumulado": "{:.2%}",
        }, na_rep="").apply(style_abc, axis=1),
        hide_index=True,
        use_container_width=True
    )
