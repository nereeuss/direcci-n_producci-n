import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Punto de Equilibrio – Dirección de Producción",
    layout="wide",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stMetricValue"] { color: #1f1f1f !important; }
[data-testid="stMetricLabel"] { color: #31333F !important; }
.stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.page-header { text-align: center; padding: 35px 30px; background-color: #312e81; border-radius: 20px; margin-bottom: 32px; box-shadow: 0 10px 40px rgba(0,0,0,0.25); }
.page-header h1 { color: #fff; font-size: 2.2rem; font-weight: 800; margin: 0 0 8px 0; text-transform: uppercase; }
.page-header p { color: #c7d2fe; font-size: 1rem; margin: 0; }
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
    <h1>TEMA 1 · PUNTO DE EQUILIBRIO</h1>
    <p>Introducción a los Sistemas Productivos — Análisis del punto de equilibrio para uno o varios productos</p>
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

# ── Mode selector ────────────────────────────────────────────────────────────
default_index = 0
if "active_ejercicio" in st.session_state:
    if "MULTIPRODUCTO" in st.session_state["active_ejercicio"]:
        default_index = 1

modo = st.selectbox(
    "SELECCIONA EL TIPO DE ANÁLISIS",
    ["1.1 PUNTO DE EQUILIBRIO — UN PRODUCTO", "1.2 PUNTO DE EQUILIBRIO — MULTIPRODUCTO"],
    index=default_index,
    key="pe_modo",
)

# ═══════════════════════════════════════════════════════════════════════════════
# 1.1  PUNTO DE EQUILIBRIO — UN PRODUCTO
# ═══════════════════════════════════════════════════════════════════════════════
if modo.startswith("1.1"):
    st.markdown("---")
    st.subheader("1.1 PUNTO DE EQUILIBRIO — UN PRODUCTO")

    # ── Input Table ─────────────────────────────────────────────────────────
    st.markdown("### DATOS DEL PRODUCTO")
    st.caption("Introduce los costes y el precio de venta unitario:")
    
    default_data_un_producto = pd.DataFrame({
        "Material (var)": [10.0],
        "Mano de obra fija": [20000.0],
        "Mano de obra variable": [15.0],
        "Costes ind. variables": [5.0],
        "Otros costes fijos": [30000.0],
        "Precio de venta": [80.0],
    })
    
    edited_dp = st.data_editor(
        default_data_un_producto,
        num_rows="fixed",
        use_container_width=True,
        hide_index=True,
        key="un_producto_editor",
        column_config={
            "Material (var)": st.column_config.NumberColumn(format="%.2f €"),
            "Mano de obra fija": st.column_config.NumberColumn(format="%.2f €"),
            "Mano de obra variable": st.column_config.NumberColumn(format="%.2f €"),
            "Costes ind. variables": st.column_config.NumberColumn(format="%.2f €"),
            "Otros costes fijos": st.column_config.NumberColumn(format="%.2f €"),
            "Precio de venta": st.column_config.NumberColumn(format="%.2f €"),
        }
    )
    
    # ── Calculations for Table 2 ─────────────────────────────────────────────
    material = edited_dp["Material (var)"].iloc[0]
    mo_fija = edited_dp["Mano de obra fija"].iloc[0]
    mo_var = edited_dp["Mano de obra variable"].iloc[0]
    civ = edited_dp["Costes ind. variables"].iloc[0]
    otros_cf = edited_dp["Otros costes fijos"].iloc[0]
    pvu = edited_dp["Precio de venta"].iloc[0]
    
    cf_total = mo_fija + otros_cf
    cvu_total = material + mo_var + civ
    
    st.markdown("### RESUMEN DE COSTES")
    resumen_costes = pd.DataFrame({
        "Concepto": ["Costes Fijos Totales (CF)", "Coste Variable Unitario Total (CVu)", "Precio de Venta (PVu)"],
        "Valor (€)": [cf_total, cvu_total, pvu]
    })
    
    def style_resumen(row):
        styles = []
        for col in resumen_costes.columns:
            if col == "Concepto":
                styles.append("background-color: #0066cc; color: white; font-weight: bold;")
            else:
                styles.append("background-color: #f8fafc; color: black;")
        return styles

    st.dataframe(resumen_costes.style.apply(style_resumen, axis=1).format({"Valor (€)": "{:,.2f}"}), hide_index=True, use_container_width=True)
    
    # ── Validation ───────────────────────────────────────────────────────────
    if pvu <= cvu_total:
        st.error("EL PRECIO DE VENTA (PVu) DEBE SER MAYOR QUE EL COSTE VARIABLE UNITARIO TOTAL (CVu) PARA OBTENER UN MARGEN POSITIVO.")
        st.stop()
        
    margen = pvu - cvu_total
    q_star = cf_total / margen
    ingreso_pe = q_star * pvu
    
    # ── Scenarios (Table 3) ──────────────────────────────────────────────────
    st.markdown("### ANÁLISIS DE ESCENARIOS (UNIDADES VENDIDAS)")
    
    # Determine optimal ranges to show around Q*
    escenarios_q = [0, int(q_star * 0.5), int(q_star * 0.8), int(q_star), int(q_star * 1.2), int(q_star * 1.5), int(q_star * 2.0)]
    escenarios_q = sorted(list(set(escenarios_q)))
    if len(escenarios_q) < 5:
        escenarios_q = [0, int(q_star), int(q_star*2), int(q_star*3), int(q_star*4)]
        escenarios_q = sorted(list(set(escenarios_q)))
        
    escenarios_data = []
    for q in escenarios_q:
        ingresos_q = q * pvu
        cv_q = q * cvu_total
        ct_q = cv_q + cf_total
        utilidad = ingresos_q - ct_q
        
        escenarios_data.append({
            "Unidades Vendidas": q,
            "Ingresos (€)": ingresos_q,
            "Costes Variables (€)": cv_q,
            "Costes Fijos (€)": cf_total,
            "Costes Totales (€)": ct_q,
            "Utilidad (€)": utilidad
        })
        
    df_escenarios = pd.DataFrame(escenarios_data)
    
    def highlight_q_star(row):
        if abs(row["Utilidad (€)"]) < 0.1:
            return ["background-color: #dbeafe; font-weight: bold; color: #1e3a8a"] * len(row)
        if row["Utilidad (€)"] < 0:
            return ["background-color: #f8fafc; color: #ef4444"] * len(row)
        return ["background-color: #f8fafc; color: #10b981"] * len(row)

    st.dataframe(
        df_escenarios.style.apply(highlight_q_star, axis=1).format({
            "Unidades Vendidas": "{:,.0f}",
            "Ingresos (€)": "{:,.2f}",
            "Costes Variables (€)": "{:,.2f}",
            "Costes Fijos (€)": "{:,.2f}",
            "Costes Totales (€)": "{:,.2f}",
            "Utilidad (€)": "{:,.2f}",
        }),
        hide_index=True,
        use_container_width=True
    )
    
    st.info(f"EL **PUNTO DE EQUILIBRIO** SE ALCANZA VENDIENDO **{q_star:,.2f}** UNIDADES, GENERANDO UNOS INGRESOS DE **{ingreso_pe:,.2f} €**.")

    # ── Chart ────────────────────────────────────────────────────────────────
    st.markdown("### GRÁFICO DEL PUNTO DE EQUILIBRIO")
    
    q_max = int(q_star * 2) if q_star > 0 else 100
    q_range = np.linspace(0, q_max, 500)
    ingresos = pvu * q_range
    costes_totales = cf_total + cvu_total * q_range
    costes_fijos = np.full_like(q_range, cf_total)

    fig = go.Figure()

    # Loss zone
    fig.add_trace(go.Scatter(
        x=np.concatenate([q_range[q_range <= q_star], q_range[q_range <= q_star][::-1]]),
        y=np.concatenate([
            (pvu * q_range[q_range <= q_star]),
            (cf_total + cvu_total * q_range[q_range <= q_star])[::-1],
        ]),
        fill="toself",
        fillcolor="rgba(239,68,68,0.12)",
        line=dict(width=0),
        name="Zona de Pérdidas",
        hoverinfo="skip",
        showlegend=True,
    ))

    # Profit zone
    fig.add_trace(go.Scatter(
        x=np.concatenate([q_range[q_range >= q_star], q_range[q_range >= q_star][::-1]]),
        y=np.concatenate([
            (pvu * q_range[q_range >= q_star]),
            (cf_total + cvu_total * q_range[q_range >= q_star])[::-1],
        ]),
        fill="toself",
        fillcolor="rgba(34,197,94,0.12)",
        line=dict(width=0),
        name="Zona de Beneficios",
        hoverinfo="skip",
        showlegend=True,
    ))

    # Lines
    cv_line = cvu_total * q_range
    u_line = ingresos - costes_totales

    fig.add_trace(go.Scatter(
        x=q_range, y=ingresos,
        mode="lines", name="Ingresos Totales",
        line=dict(color="#6366f1", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=q_range, y=cv_line,
        mode="lines", name="Costes Variables",
        line=dict(color="#f97316", width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=q_range, y=costes_totales,
        mode="lines", name="Costes Totales",
        line=dict(color="#ef4444", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=q_range, y=costes_fijos,
        mode="lines", name="Costes Fijos",
        line=dict(color="#94a3b8", width=2, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=q_range, y=u_line,
        mode="lines", name="Utilidad",
        line=dict(color="#10b981", width=2),
    ))

    # Intersection point
    fig.add_trace(go.Scatter(
        x=[q_star], y=[ingreso_pe],
        mode="markers+text",
        marker=dict(size=14, color="#312e81", symbol="diamond", line=dict(width=2, color="#fff")),
        text=[f"Q*={q_star:,.1f}"],
        textposition="top right",
        textfont=dict(size=13, color="#312e81", family="Inter"),
        name="Punto de Equilibrio",
        showlegend=True,
    ))

    fig.update_layout(
        title=dict(text="ANÁLISIS DEL PUNTO DE EQUILIBRIO", font=dict(size=18, family="Inter")),
        xaxis_title="CANTIDAD (Q)",
        yaxis_title="€",
        template="plotly_white",
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
        yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
        height=520,
        legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5),
        margin=dict(t=80, b=120),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 1.2  PUNTO DE EQUILIBRIO — MULTIPRODUCTO
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown("---")
    st.subheader("1.2 PUNTO DE EQUILIBRIO — MULTIPRODUCTO")

    # ── Parámetros globales ──────────────────────────────────────────────────
    st.markdown("### PARÁMETROS GLOBALES")
    cf_multi = st.number_input("COSTE FIJO TOTAL (CF)", min_value=0.0, value=3800000.0, step=100.0, format="%.2f")

    # ── Editable table (Inputs) ──────────────────────────────────────────────
    st.markdown("### DATOS DE LOS PRODUCTOS (ENTRADA)")
    st.caption("Introduce los datos básicos de cada producto. Añade o elimina filas según necesites.")
    
    default_data = pd.DataFrame({
        "Producto": ["Producto A", "Producto B", "Producto C"],
        "PVu (€/ud)": [20.0, 15.0, 10.0],
        "CVu (€/ud)": [8.0, 6.0, 5.0],
        "Demanda (Q)": [120, 79, 50],
    })

    edited_df = st.data_editor(
        default_data,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="multi_pe_editor",
        column_config={
            "Producto": st.column_config.TextColumn("Producto", width="medium"),
            "PVu (€/ud)": st.column_config.NumberColumn("PVu (€/ud)", min_value=0.0, format="%.2f"),
            "CVu (€/ud)": st.column_config.NumberColumn("CVu (€/ud)", min_value=0.0, format="%.2f"),
            "Demanda (Q)": st.column_config.NumberColumn("Demanda (Q)", min_value=1, step=1),
        },
    )

    # ── Validation ───────────────────────────────────────────────────────────
    if edited_df.empty or edited_df["Demanda (Q)"].sum() == 0:
        st.warning("INTRODUCE AL MENOS UN PRODUCTO CON DEMANDA MAYOR A 0.")
        st.stop()

    invalid_margins = edited_df[edited_df["PVu (€/ud)"] <= edited_df["CVu (€/ud)"]]
    if not invalid_margins.empty:
        st.error(f"EL PRECIO DE VENTA (PVu) DEBE SER MAYOR QUE EL COSTE VARIABLE (CVu). REVISA: {', '.join(invalid_margins['Producto'].tolist())}")
        st.stop()

    # ── Calculations (Algebraic Method) ──────────────────────────────────────
    df_calc = edited_df.copy()
    q_tot = df_calc["Demanda (Q)"].sum()
    
    df_calc["% Participación"] = df_calc["Demanda (Q)"] / q_tot
    df_calc["MCu = Pvu - Cvu"] = df_calc["PVu (€/ud)"] - df_calc["CVu (€/ud)"]
    df_calc["MCP"] = df_calc["MCu = Pvu - Cvu"] * df_calc["% Participación"]
    
    mcp_tot = df_calc["MCP"].sum()
    qe_total = cf_multi / mcp_tot
    
    df_calc["Qe"] = qe_total * df_calc["% Participación"]
    df_calc["Ingresos (€)"] = df_calc["Qe"] * df_calc["PVu (€/ud)"]
    
    i_tot = df_calc["Ingresos (€)"].sum()
    
    # Create algebraic table with Totals row
    df_algebraico = df_calc.copy()
    df_algebraico["CF"] = np.nan
    if len(df_algebraico) > 0:
        df_algebraico.loc[0, "CF"] = cf_multi
        
    df_algebraico = df_algebraico[["Producto", "PVu (€/ud)", "CVu (€/ud)", "CF", "Demanda (Q)", "% Participación", "MCu = Pvu - Cvu", "MCP"]]
    
    df_algebraico.loc["TOTAL"] = {
        "Producto": "TOTAL",
        "PVu (€/ud)": np.nan,
        "CVu (€/ud)": np.nan,
        "CF": np.nan,
        "Demanda (Q)": q_tot,
        "% Participación": 1.0,
        "MCu = Pvu - Cvu": np.nan,
        "MCP": mcp_tot,
    }

    st.markdown("### 1. MÉTODO ALGEBRAICO (RESULTADOS)")
    
    def style_total_alg(row):
        styles = []
        for col in df_algebraico.columns:
            if col == "Producto":
                if row.name == "TOTAL":
                    styles.append('background-color: #d9d9d9; font-weight: bold; color: #0066cc; border-top: 2px solid #0066cc;')
                else:
                    styles.append('background-color: #0066cc; color: white; font-weight: bold;')
            else:
                if row.name == "TOTAL":
                    styles.append('background-color: #d9d9d9; font-weight: bold; color: #000000; border-top: 2px solid #0066cc;')
                else:
                    styles.append('background-color: #f8fafc; color: black;')
        return styles

    st.dataframe(
        df_algebraico.style.format({
            "PVu (€/ud)": "{:,.2f}",
            "CVu (€/ud)": "{:,.2f}",
            "CF": "{:,.2f}",
            "Demanda (Q)": "{:,.1f}",
            "% Participación": "{:.2%}",
            "MCu = Pvu - Cvu": "{:,.2f}",
            "MCP": "{:,.2f}",
        }, na_rep="").apply(style_total_alg, axis=1),
        hide_index=True,
        use_container_width=True
    )
    
    # ── Calculations (Weighted Method) ───────────────────────────────────────
    df_pond = pd.DataFrame()
    df_pond["Producto"] = df_calc["Producto"]
    df_pond["Qe"] = df_calc["Qe"]
    df_pond["Ingresos (€)"] = df_calc["Ingresos (€)"]
    df_pond["PVpond"] = df_calc["PVu (€/ud)"] * df_calc["% Participación"]
    df_pond["CVpond"] = df_calc["CVu (€/ud)"] * df_calc["% Participación"]
    
    pv_pond_tot = df_pond["PVpond"].sum()
    cv_pond_tot = df_pond["CVpond"].sum()
    
    ie_1 = qe_total * pv_pond_tot
    ie_2 = cf_multi / (1 - (cv_pond_tot / pv_pond_tot))
    
    df_pond["IE(I)"] = ""
    df_pond["IE(II)"] = ""
    if len(df_pond) > 0:
        df_pond.loc[0, "IE(I)"] = f"{ie_1:,.1f}"
        df_pond.loc[0, "IE(II)"] = f"{ie_2:,.1f}"
    
    df_pond_display = df_pond.copy()
    df_pond_display.loc["TOTAL"] = {
        "Producto": "TOTAL",
        "Qe": qe_total,
        "Ingresos (€)": i_tot,
        "PVpond": pv_pond_tot,
        "CVpond": cv_pond_tot,
        "IE(I)": "Coincide" if abs(ie_1 - ie_2) < 0.1 else "No coincide",
        "IE(II)": "Coincide" if abs(ie_1 - ie_2) < 0.1 else "No coincide"
    }

    def style_total_pond(row):
        styles = []
        for col in df_pond_display.columns:
            if col == "Producto":
                if row.name == "TOTAL":
                    styles.append('background-color: #d9d9d9; font-weight: bold; color: #0066cc; border-top: 2px solid #0066cc;')
                else:
                    styles.append('background-color: #0066cc; color: white; font-weight: bold;')
            elif col in ["IE(I)", "IE(II)"]:
                if row.name == "TOTAL" and "Coincide" in str(row[col]):
                    styles.append('background-color: #86efac; color: black; font-weight: bold; text-align: center; border-top: 2px solid #0066cc;') # Green
                else:
                    styles.append('background-color: #f8fafc; color: black; text-align: center;')
            else:
                if row.name == "TOTAL":
                    styles.append('background-color: #d9d9d9; font-weight: bold; color: #000000; border-top: 2px solid #0066cc;')
                else:
                    styles.append('background-color: #f8fafc; color: black;')
        return styles

    st.markdown("### 2. MÉTODO PONDERADO")
    st.dataframe(
        df_pond_display.style.format({
            "Qe": "{:,.1f}",
            "Ingresos (€)": "{:,.1f}",
            "PVpond": "{:,.2f}",
            "CVpond": "{:,.2f}",
        }, na_rep="").apply(style_total_pond, axis=1),
        hide_index=True,
        use_container_width=True
    )

    # ── Scenarios (Table & Chart) ────────────────────────────────────────────
    st.markdown("### MÉTODO GRÁFICO Y ESCENARIOS (Qe global)")
    
    # Generate scenarios based on Qe_total
    step = max(5000, int(qe_total * 0.1) // 5000 * 5000)
    if step == 0: step = 5000
    start_q = max(step, (int(qe_total) // step - 2) * step)
    end_q = start_q + step * 8
    
    escenarios_q = list(range(start_q, end_q, step))
    if int(qe_total) not in escenarios_q:
        escenarios_q.append(int(qe_total))
    escenarios_q = sorted(list(set(escenarios_q)))
    
    escenarios_data = []
    for q in escenarios_q:
        ingresos_q = q * pv_pond_tot
        cv_q = q * cv_pond_tot
        ct_q = cv_q + cf_multi
        utilidad = ingresos_q - ct_q
        
        escenarios_data.append({
            "Qe": q,
            "I": ingresos_q,
            "CV": cv_q,
            "CF": cf_multi,
            "CT": ct_q,
            "U = I-CT": utilidad
        })
        
    df_escenarios = pd.DataFrame(escenarios_data)
    
    def highlight_q_star_multi(row):
        styles = []
        for col in df_escenarios.columns:
            if col == "Qe":
                styles.append("background-color: #0066cc; color: white; font-weight: bold;")
            elif col == "U = I-CT" and row["U = I-CT"] < 0:
                styles.append("background-color: #f8fafc; color: #ef4444; font-weight: bold;")
            elif col == "U = I-CT" and abs(row["U = I-CT"]) < (pv_pond_tot * 0.5):
                styles.append("background-color: #dbeafe; font-weight: bold; color: #1e3a8a;")
            else:
                styles.append("background-color: #f8fafc; color: black;")
        return styles

    st.markdown("### 3. ESCENARIOS (Qe global)")
    st.dataframe(
        df_escenarios.style.apply(highlight_q_star_multi, axis=1).format({
            "Qe": "{:,.1f}",
            "I": "{:,.1f}",
            "CV": "{:,.1f}",
            "CF": "{:,.1f}",
            "CT": "{:,.1f}",
            "U = I-CT": "{:,.1f}",
        }),
        hide_index=True,
        use_container_width=True
    )

    # ── Chart ────────────────────────────────────────────────────────────────
    q_range = np.linspace(start_q, end_q, 200)
    ingresos_line = q_range * pv_pond_tot
    cv_line = q_range * cv_pond_tot
    ct_line = cv_line + cf_multi
    cf_line = np.full_like(q_range, cf_multi)
    u_line = ingresos_line - ct_line

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=q_range, y=ingresos_line, mode="lines", name="Ingresos (I)", line=dict(color="#3b82f6", width=3)))
    fig.add_trace(go.Scatter(x=q_range, y=cv_line, mode="lines", name="Coste Variable (CV)", line=dict(color="#f97316", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=q_range, y=cf_line, mode="lines", name="Costes Fijos (CF)", line=dict(color="#94a3b8", width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=q_range, y=ct_line, mode="lines", name="Costes Totales (CT)", line=dict(color="#eab308", width=3)))
    fig.add_trace(go.Scatter(x=q_range, y=u_line, mode="lines", name="Utilidad (U)", line=dict(color="#10b981", width=2)))

    # Intersection point
    fig.add_trace(go.Scatter(
        x=[qe_total], y=[ie_1],
        mode="markers+text",
        marker=dict(size=14, color="#1e3a8a", symbol="diamond", line=dict(width=2, color="#fff")),
        text=[f"Qe={qe_total:,.1f}"],
        textposition="top left",
        textfont=dict(size=13, color="#1e3a8a", family="Inter"),
        name="Punto de Equilibrio",
        showlegend=True,
    ))

    fig.update_layout(
        title=dict(text="PUNTO DE EQUILIBRIO MULTIPRODUCTO", font=dict(size=18, family="Inter")),
        xaxis_title="CANTIDAD TOTAL DE EQUILIBRIO (Qe)",
        yaxis_title="€",
        template="plotly_white",
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
        yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5),
        margin=dict(t=80, b=60),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
