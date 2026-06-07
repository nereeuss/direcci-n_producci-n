import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy.optimize import linprog
from math import ceil
from itertools import combinations

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Lean Manufacturing", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stMetricValue"] { color: #1f1f1f !important; }
[data-testid="stMetricLabel"] { color: #31333F !important; }
.stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.page-header { text-align: center; padding: 35px 30px; background-color: #dc2626; border-radius: 20px; margin-bottom: 32px; box-shadow: 0 10px 40px rgba(127,29,29,0.30); }
.page-header h1 { color: #fff; font-size: 2.2rem; font-weight: 800; margin: 0 0 8px 0; text-transform: uppercase; }
.page-header p { color: #fca5a5; font-size: 1rem; margin: 0; }
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
    <h1>TEMA 8 · LEAN MANUFACTURING</h1>
    <p>Takt Time, Programación Lineal y Cuellos de Botella</p>
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

# ── Exercise selector ────────────────────────────────────────────────────────
default_idx = 0
if "active_ejercicio" in st.session_state:
    if "SIMPLEX" in st.session_state["active_ejercicio"]:
        default_idx = 1
    elif "CUELLOS" in st.session_state["active_ejercicio"]:
        default_idx = 2
        
ejercicio = st.selectbox(
    "SELECCIONA UN EJERCICIO",
    ["8.1 Takt Time y Tiempo de Ciclo",
     "8.2 Simplex para 2 Variables",
     "8.3 Capacidad de Planta y Cuellos de Botella"],
    index=default_idx,
    key="lean_ejercicio",
)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 8.1 — TAKT TIME Y TIEMPO DE CICLO
# ══════════════════════════════════════════════════════════════════════════════
if ejercicio == "8.1 Takt Time y Tiempo de Ciclo":
    try:
        st.markdown("### DATOS DE ENTRADA")
        c_in1, c_in2 = st.columns([1.5, 1])
        
        with c_in1:
            if "df_takt_params" not in st.session_state:
                st.session_state.df_takt_params = pd.DataFrame({
                    "Parámetro": [
                        "Demanda cliente", "Días laborables", "Disponibilidad máquina (%)", 
                        "Defectuosos (%)", "Jornada diaria (h)", "Turnos de trabajo", 
                        "Tiempo descanso (min)", "Tiempo cambio turno (min)", "Productos por paquete"
                    ],
                    "Valor": [40000.0, 20.0, 83.0, 3.0, 8.0, 3.0, 30.0, 20.0, 12.0],
                    "Unidad": [
                        "prod/mes", "dia/mes", "%", "%", "h/dia", "turnos/dia", "min/turno", "min/turno", "prod/paq"
                    ]
                })
            
            st.markdown("**PARÁMETROS GLOBALES**")
            ed_params = st.data_editor(
                st.session_state.df_takt_params,
                use_container_width=True, hide_index=True,
                column_config={
                    "Parámetro": st.column_config.TextColumn("Parámetro", disabled=True),
                    "Valor": st.column_config.NumberColumn("Valor", min_value=0.0, format="%.2f"),
                    "Unidad": st.column_config.TextColumn("Unidad", disabled=True)
                }
            )
            st.session_state.df_takt_params = ed_params
            
        with c_in2:
            if "df_takt_procesos" not in st.session_state:
                st.session_state.df_takt_procesos = pd.DataFrame({
                    "Proceso": ["A", "B", "C", "D"],
                    "Tiempo ciclo (seg)": [34.0, 45.0, 4.0, 25.0]
                })
            
            st.markdown("**PROCESOS Y TIEMPOS DE CICLO**")
            ed_proc = st.data_editor(
                st.session_state.df_takt_procesos,
                use_container_width=True, hide_index=True, num_rows="dynamic",
                column_config={
                    "Proceso": st.column_config.TextColumn("Proceso", required=True),
                    "Tiempo ciclo (seg)": st.column_config.NumberColumn("Tiempo ciclo (seg)", min_value=0.0, required=True)
                }
            )
            st.session_state.df_takt_procesos = ed_proc

        st.divider()
        st.markdown("### RESOLUCIÓN")
        
        # Extract values
        val = dict(zip(ed_params["Parámetro"], ed_params["Valor"]))
        demanda = val["Demanda cliente"]
        dias_mes = val["Días laborables"]
        disp = val["Disponibilidad máquina (%)"] / 100.0
        defect = val["Defectuosos (%)"] / 100.0
        jornada = val["Jornada diaria (h)"]
        turnos = val["Turnos de trabajo"]
        descanso = val["Tiempo descanso (min)"]
        cambio = val["Tiempo cambio turno (min)"]
        paquete = val["Productos por paquete"]

        # Calculations
        tiempo_disp_bruto = jornada * 60 * turnos
        tiempo_improd = turnos * (descanso + cambio)
        tiempo_neto_dia = (tiempo_disp_bruto - tiempo_improd) * disp
        
        demanda_mensual_total = demanda * (1 + defect)
        demanda_diaria_total = demanda_mensual_total / dias_mes if dias_mes > 0 else 0
        
        takt_time_min = tiempo_neto_dia / demanda_diaria_total if demanda_diaria_total > 0 else 0
        takt_time_seg = takt_time_min * 60
        
        takt_time_paq_min = takt_time_min * paquete
        takt_time_paq_seg = takt_time_seg * paquete

        # Results Layout
        cr1, cr2 = st.columns([1, 1.5])
        
        with cr1:
            # Intermediate table
            df_inter = pd.DataFrame({
                "Concepto": ["Demanda cliente total mensual", "Demanda cliente total diaria", "Tiempo neto disponible"],
                "Cantidad": [demanda_mensual_total, demanda_diaria_total, tiempo_neto_dia],
                "Unidad": ["prod/mes", "prod/dia", "min/dia"]
            })
            st.markdown("**CÁLCULOS INTERMEDIOS**")
            st.dataframe(
                df_inter.style.apply(lambda row: ["background-color: #0066cc; color: white; font-weight: bold; text-align: center;"] + ["background-color: #f8fafc; color: black; text-align: center;"] * 2, axis=1).format({"Cantidad": "{:.0f}"}),
                use_container_width=True, hide_index=True
            )
            
            st.latex(r"Takt \ time = \frac{Tiempo \ neto \ disponible}{Demanda \ del \ cliente + Defectuosos}")
            
            st.markdown(f"**Takt time prod** = `{takt_time_min:.2f} min/prod` = `{takt_time_seg:.2f} seg/prod`")
            st.markdown(f"**Takt time paq** = `{takt_time_paq_min:.2f} min/paq` = `{takt_time_paq_seg:.2f} seg/paq`")

        with cr2:
            st.markdown("**ANÁLISIS DE CAPACIDAD**")
            df_res = ed_proc.dropna(subset=["Proceso", "Tiempo ciclo (seg)"]).copy()
            df_res["Tiempo ciclo"] = pd.to_numeric(df_res["Tiempo ciclo (seg)"], errors="coerce")
            df_res["Takt time"] = takt_time_seg
            df_res["Unidad"] = "seg/prod"
            df_res["Capacidad productiva"] = df_res.apply(lambda x: "Cuello botella" if x["Tiempo ciclo"] > x["Takt time"] else "Capacidad correcta", axis=1)
            
            def style_capacidad(row):
                styles = ["background-color: #0066cc; color: white; font-weight: bold; text-align: center;"]
                styles += ["background-color: #f8fafc; color: black; text-align: center;"] * 3
                if row["Capacidad productiva"] == "Cuello botella":
                    styles.append("background-color: #fca5a5; color: #991b1b; font-weight: bold; text-align: center;")
                else:
                    styles.append("background-color: #d1fae5; color: #065f46; font-weight: bold; text-align: center;")
                return styles
            
            st.dataframe(
                df_res[["Proceso", "Tiempo ciclo", "Takt time", "Unidad", "Capacidad productiva"]].style.apply(style_capacidad, axis=1).format({"Tiempo ciclo": "{:.0f}", "Takt time": "{:.2f}"}),
                use_container_width=True, hide_index=True
            )
            
            # Chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_res["Proceso"], y=df_res["Tiempo ciclo"],
                name="Tiempo ciclo",
                marker_color="#3b82f6"
            ))
            fig.add_trace(go.Scatter(
                x=df_res["Proceso"], y=df_res["Takt time"],
                name="Takt time",
                mode="lines", line=dict(color="white", width=4),
            ))
            fig.update_layout(
                title="Takt time y tiempo de ciclo",
                barmode="overlay",
                plot_bgcolor="#1f1f1f", paper_bgcolor="#1f1f1f",
                font=dict(color="white"),
                legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=40, b=80, l=10, r=10)
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor="#333333")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"SE HA PRODUCIDO UN ERROR: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 8.2 — SIMPLEX PARA 2 VARIABLES (MÉTODO GRÁFICO)
# ══════════════════════════════════════════════════════════════════════════════
elif ejercicio == "8.2 Simplex para 2 Variables":
    try:
        with st.sidebar:
            st.header("PARÁMETROS — SIMPLEX")
            tipo = st.selectbox("Tipo de optimización", ["Maximizar", "Minimizar"])
            st.markdown("**Función Objetivo:** Z = c₁·x₁ + c₂·x₂")
            c1 = st.number_input("Coeficiente c₁", value=5.0, step=1.0)
            c2 = st.number_input("Coeficiente c₂", value=4.0, step=1.0)
            num_constraints = st.slider("Número de restricciones", 1, 10, 2)

        st.subheader("RESTRICCIONES")
        st.caption("Define las restricciones del problema. Las condiciones x₁ ≥ 0, x₂ ≥ 0 se asumen implícitamente.")

        # Build default constraint data
        default_constraints = pd.DataFrame({
            "a1": [6.0, 1.0] + [0.0] * max(0, num_constraints - 2),
            "a2": [4.0, 2.0] + [0.0] * max(0, num_constraints - 2),
            "Tipo": ["≤", "≤"] + ["≤"] * max(0, num_constraints - 2),
            "b": [24.0, 6.0] + [0.0] * max(0, num_constraints - 2),
        })
        default_constraints = default_constraints.iloc[:num_constraints]

        df_constraints = st.data_editor(
            default_constraints,
            use_container_width=True,
            key="constraints_editor",
            hide_index=True,
            column_config={
                "a1": st.column_config.NumberColumn("a₁", required=True, format="%.2f"),
                "a2": st.column_config.NumberColumn("a₂", required=True, format="%.2f"),
                "Tipo": st.column_config.SelectboxColumn("Tipo", options=["≤", "≥", "="], required=True),
                "b": st.column_config.NumberColumn("b (RHS)", required=True, format="%.2f"),
            },
        )

        st.markdown(f"**Función Objetivo:** {'Max' if tipo == 'Maximizar' else 'Min'} Z = {c1}·x₁ + {c2}·x₂")

        # Display constraint equations
        for i, row in df_constraints.iterrows():
            st.markdown(f"  Restricción {i+1}: {row['a1']}·x₁ + {row['a2']}·x₂ {row['Tipo']} {row['b']}")
        st.markdown("  x₁ ≥ 0, x₂ ≥ 0")

        st.divider()

        # ── Solve with scipy ─────────────────────────────────────────────────
        n_cons = len(df_constraints)

        # Prepare for linprog (minimization)
        c_obj = np.array([c1, c2])
        if tipo == "Maximizar":
            c_linprog = -c_obj  # negate for max
        else:
            c_linprog = c_obj

        A_ub_list = []
        b_ub_list = []
        A_eq_list = []
        b_eq_list = []

        for _, row in df_constraints.iterrows():
            a_row = [row["a1"], row["a2"]]
            b_val = row["b"]
            if row["Tipo"] == "≤":
                A_ub_list.append(a_row)
                b_ub_list.append(b_val)
            elif row["Tipo"] == "≥":
                A_ub_list.append([-a_row[0], -a_row[1]])
                b_ub_list.append(-b_val)
            elif row["Tipo"] == "=":
                A_eq_list.append(a_row)
                b_eq_list.append(b_val)

        A_ub = np.array(A_ub_list) if A_ub_list else None
        b_ub = np.array(b_ub_list) if b_ub_list else None
        A_eq = np.array(A_eq_list) if A_eq_list else None
        b_eq = np.array(b_eq_list) if b_eq_list else None

        bounds = [(0, None), (0, None)]

        result = linprog(c_linprog, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

        if not result.success:
            st.error(f"EL PROBLEMA NO TIENE SOLUCIÓN FACTIBLE O ES NO ACOTADO. ESTADO: {result.message}")
            st.stop()

        opt_x1, opt_x2 = result.x
        opt_z = c1 * opt_x1 + c2 * opt_x2

        # ── Find all corner points (intersections) ───────────────────────────
        # Build list of all lines: constraints + axes (x1=0, x2=0)
        lines = []
        for _, row in df_constraints.iterrows():
            lines.append((row["a1"], row["a2"], row["b"]))
        # Add axes
        lines.append((1.0, 0.0, 0.0))  # x1 = 0
        lines.append((0.0, 1.0, 0.0))  # x2 = 0

        def satisfies_all(x1_val, x2_val):
            """Check if point satisfies all constraints and non-negativity."""
            if x1_val < -1e-9 or x2_val < -1e-9:
                return False
            for _, row in df_constraints.iterrows():
                lhs = row["a1"] * x1_val + row["a2"] * x2_val
                rhs = row["b"]
                if row["Tipo"] == "≤" and lhs > rhs + 1e-9:
                    return False
                elif row["Tipo"] == "≥" and lhs < rhs - 1e-9:
                    return False
                elif row["Tipo"] == "=" and abs(lhs - rhs) > 1e-9:
                    return False
            return True

        corner_points = []
        for (a1_1, a2_1, b_1), (a1_2, a2_2, b_2) in combinations(lines, 2):
            A_mat = np.array([[a1_1, a2_1], [a1_2, a2_2]])
            b_vec = np.array([b_1, b_2])
            det = np.linalg.det(A_mat)
            if abs(det) < 1e-12:
                continue  # parallel or coincident
            sol = np.linalg.solve(A_mat, b_vec)
            x1_s, x2_s = sol
            if satisfies_all(x1_s, x2_s):
                # Round to avoid floating point duplicates
                x1_r = round(x1_s, 6)
                x2_r = round(x2_s, 6)
                # Check for duplicates
                is_dup = False
                for px_val, py_val, _ in corner_points:
                    if abs(px_val - x1_r) < 1e-6 and abs(py_val - x2_r) < 1e-6:
                        is_dup = True
                        break
                if not is_dup:
                    z_val = c1 * x1_r + c2 * x2_r
                    corner_points.append((x1_r, x2_r, round(z_val, 6)))

        if not corner_points:
            st.error("NO SE ENCONTRARON PUNTOS FACTIBLES. REVISA LAS RESTRICCIONES.")
            st.stop()

        # ── Metrics ──────────────────────────────────────────────────────────
        st.subheader("SOLUCIÓN ÓPTIMA")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("x₁ óptimo", f"{opt_x1:.4f}")
        mc2.metric("x₂ óptimo", f"{opt_x2:.4f}")
        mc3.metric(f"Z {'máximo' if tipo == 'Maximizar' else 'mínimo'}", f"{opt_z:.4f}")

        # ── Corner points table ──────────────────────────────────────────────
        st.subheader("PUNTOS ESQUINA DEL POLÍGONO FACTIBLE")
        df_corners = pd.DataFrame(corner_points, columns=["x₁", "x₂", "Z"])
        df_corners = df_corners.sort_values("Z", ascending=(tipo == "Minimizar")).reset_index(drop=True)

        # Highlight optimal row
        if tipo == "Maximizar":
            best_z = df_corners["Z"].max()
        else:
            best_z = df_corners["Z"].min()

        def highlight_optimal(row):
            if abs(row["Z"] - best_z) < 1e-6:
                return ["background-color: #d1fae5; font-weight: bold; color: black;"] * len(row)
            return ["background-color: #f8fafc; color: black;"] * len(row)

        st.dataframe(
            df_corners.style.apply(highlight_optimal, axis=1).format({"x₁": "{:.4f}", "x₂": "{:.4f}", "Z": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )

        # ── Graphical plot ───────────────────────────────────────────────────
        st.subheader("MÉTODO GRÁFICO")

        # Determine axis range
        all_x1 = [p[0] for p in corner_points]
        all_x2 = [p[1] for p in corner_points]
        max_x1 = max(max(all_x1) * 1.5, 1)
        max_x2 = max(max(all_x2) * 1.5, 1)

        fig = go.Figure()

        # Plot constraint lines
        constraint_colors = px.colors.qualitative.Set2
        x1_range = np.linspace(0, max_x1, 400)

        for i, (_, row) in enumerate(df_constraints.iterrows()):
            a1_c, a2_c, b_c = row["a1"], row["a2"], row["b"]
            color = constraint_colors[i % len(constraint_colors)]

            if abs(a2_c) > 1e-12:
                x2_line = (b_c - a1_c * x1_range) / a2_c
                mask = (x2_line >= -0.5) & (x1_range >= -0.5)
                fig.add_trace(go.Scatter(
                    x=x1_range[mask], y=x2_line[mask],
                    mode="lines",
                    name=f"R{i+1}: {a1_c}x₁+{a2_c}x₂{row['Tipo']}{b_c}",
                    line=dict(color=color, width=2),
                ))
            elif abs(a1_c) > 1e-12:
                x1_val = b_c / a1_c
                fig.add_trace(go.Scatter(
                    x=[x1_val, x1_val], y=[0, max_x2],
                    mode="lines",
                    name=f"R{i+1}: {a1_c}x₁{row['Tipo']}{b_c}",
                    line=dict(color=color, width=2),
                ))

        # Sort corner points by angle for polygon fill
        cx = np.mean(all_x1)
        cy = np.mean(all_x2)
        angles = [np.arctan2(p[1] - cy, p[0] - cx) for p in corner_points]
        sorted_idx = np.argsort(angles)
        polygon_x = [corner_points[i][0] for i in sorted_idx] + [corner_points[sorted_idx[0]][0]]
        polygon_y = [corner_points[i][1] for i in sorted_idx] + [corner_points[sorted_idx[0]][1]]

        # Feasible region
        fig.add_trace(go.Scatter(
            x=polygon_x, y=polygon_y,
            fill="toself",
            fillcolor="rgba(59, 130, 246, 0.15)",
            line=dict(color="rgba(59, 130, 246, 0.5)", width=2),
            name="Región Factible",
        ))

        # Corner points
        fig.add_trace(go.Scatter(
            x=[p[0] for p in corner_points],
            y=[p[1] for p in corner_points],
            mode="markers+text",
            marker=dict(color="#3b82f6", size=10, line=dict(color="#fff", width=1)),
            text=[f"({p[0]:.2f}, {p[1]:.2f})<br>Z={p[2]:.2f}" for p in corner_points],
            textposition="top center",
            textfont=dict(size=10),
            name="Puntos Esquina",
        ))

        # Optimal point
        fig.add_trace(go.Scatter(
            x=[opt_x1], y=[opt_x2],
            mode="markers+text",
            marker=dict(symbol="star", color="#f59e0b", size=20, line=dict(color="#000", width=1.5)),
            text=[f"ÓPTIMO<br>({opt_x1:.2f}, {opt_x2:.2f})<br>Z={opt_z:.2f}"],
            textposition="top center",
            textfont=dict(size=12, color="#b45309"),
            name="Punto Óptimo",
        ))

        # Iso-profit / iso-cost line at optimum
        if abs(c2) > 1e-12:
            iso_x2 = (opt_z - c1 * x1_range) / c2
            mask = (iso_x2 >= -0.5) & (x1_range >= -0.5) & (iso_x2 <= max_x2 * 1.2)
            fig.add_trace(go.Scatter(
                x=x1_range[mask], y=iso_x2[mask],
                mode="lines",
                name=f"Iso-{'beneficio' if tipo == 'Maximizar' else 'coste'} Z={opt_z:.2f}",
                line=dict(color="#f59e0b", width=2, dash="dash"),
            ))
        elif abs(c1) > 1e-12:
            x1_iso = opt_z / c1
            fig.add_trace(go.Scatter(
                x=[x1_iso, x1_iso], y=[0, max_x2],
                mode="lines",
                name=f"Iso-{'beneficio' if tipo == 'Maximizar' else 'coste'} Z={opt_z:.2f}",
                line=dict(color="#f59e0b", width=2, dash="dash"),
            ))

        fig.update_layout(
            title="REGIÓN FACTIBLE Y SOLUCIÓN ÓPTIMA",
            xaxis_title="x₁",
            yaxis_title="x₂",
            xaxis=dict(range=[-0.3, max_x1], zeroline=True, zerolinecolor="black", zerolinewidth=2, showline=True, linewidth=2, linecolor='black', mirror=True),
            yaxis=dict(range=[-0.3, max_x2], zeroline=True, zerolinecolor="black", zerolinewidth=2, showline=True, linewidth=2, linecolor='black', mirror=True),
            height=600,
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='white',
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"SE HA PRODUCIDO UN ERROR: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 8.3 — CAPACIDAD DE PLANTA Y CUELLOS DE BOTELLA
# ══════════════════════════════════════════════════════════════════════════════
elif ejercicio == "8.3 Capacidad de Planta y Cuellos de Botella":
    try:
        st.markdown("### DATOS DE ENTRADA")
        
        # Init state
        if "df_cap_tiempos" not in st.session_state:
            st.session_state.df_cap_tiempos = pd.DataFrame({
                "Planta": ["V", "W", "X", "Y", "Z"],
                "Producto A": [30.0, 0.0, 10.0, 10.0, 0.0],
                "Producto B": [0.0, 0.0, 20.0, 10.0, 0.0],
                "Producto C": [0.0, 5.0, 5.0, 5.0, 5.0],
                "Producto D": [0.0, 15.0, 0.0, 5.0, 10.0]
            })
        if "df_cap_demanda" not in st.session_state:
            st.session_state.df_cap_demanda = pd.DataFrame({
                "Producto": ["Producto A", "Producto B", "Producto C", "Producto D"],
                "Demanda (ud/sem)": [60, 80, 80, 100]
            })
        if "jornada_h" not in st.session_state:
            st.session_state.jornada_h = 40.0
            
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown("**TIEMPOS POR PRODUCTO Y PLANTA (min/ud)**")
            c_add, c_rm = st.columns(2)
            with c_add:
                if st.button("+ AÑADIR PRODUCTO", use_container_width=True):
                    n = len(st.session_state.df_cap_tiempos.columns)
                    pname = f"Producto {chr(64 + n)}" # A, B, C...
                    st.session_state.df_cap_tiempos[pname] = 0.0
                    st.session_state.df_cap_demanda.loc[len(st.session_state.df_cap_demanda)] = [pname, 0]
                    st.rerun()
            with c_rm:
                if st.button("- ELIMINAR PRODUCTO", use_container_width=True):
                    if len(st.session_state.df_cap_tiempos.columns) > 2:
                        last_col = st.session_state.df_cap_tiempos.columns[-1]
                        st.session_state.df_cap_tiempos.drop(columns=[last_col], inplace=True)
                        st.session_state.df_cap_demanda = st.session_state.df_cap_demanda.iloc[:-1]
                        st.rerun()
                        
            ed_tiempos = st.data_editor(st.session_state.df_cap_tiempos, num_rows="dynamic", use_container_width=True, hide_index=True)
            st.session_state.df_cap_tiempos = ed_tiempos
            
        with c2:
            st.markdown("**DEMANDA SEMANAL**")
            ed_demanda = st.data_editor(st.session_state.df_cap_demanda, use_container_width=True, hide_index=True)
            st.session_state.df_cap_demanda = ed_demanda
            
        with c3:
            st.markdown("**PARÁMETROS GLOBALES**")
            jornada = st.number_input("Jornada semanal (h/sem)", value=st.session_state.jornada_h, step=1.0)
            st.session_state.jornada_h = jornada
            
        st.divider()
        st.markdown("### RESOLUCIÓN")
        
        # Calculations
        capacidad_disp_min = jornada * 60
        
        df_clean = ed_tiempos.dropna(subset=["Planta"])
        productos = [c for c in df_clean.columns if c != "Planta"]
        
        cols = ["Planta"]
        for p in productos:
            cols.extend([f"{p} (min/ud)", f"{p} (min/sem)"])
        cols.extend(["TOTAL min/sem", "CAPACIDAD PRODUCTIVA"])
        
        res_data = []
        for i, row in df_clean.iterrows():
            planta = row["Planta"]
            row_dict = {"Planta": planta}
            total_min = 0
            
            for p in productos:
                min_ud = row[p]
                demanda_val = 0
                dem_row = ed_demanda[ed_demanda["Producto"] == p]
                if not dem_row.empty:
                    demanda_val = pd.to_numeric(dem_row.iloc[0]["Demanda (ud/sem)"], errors="coerce")
                    if np.isnan(demanda_val): demanda_val = 0
                
                min_sem = min_ud * demanda_val
                total_min += min_sem
                
                row_dict[f"{p} (min/ud)"] = min_ud
                row_dict[f"{p} (min/sem)"] = min_sem
                
            row_dict["TOTAL min/sem"] = total_min
            row_dict["CAPACIDAD PRODUCTIVA"] = "Cuello de botella" if total_min > capacidad_disp_min else "Capacidad correcta"
            res_data.append(row_dict)
            
        df_res = pd.DataFrame(res_data)
        
        def style_capacidad_planta(row):
            styles = []
            for col in df_res.columns:
                if col == "Planta":
                    styles.append("background-color: #0066cc; color: white; font-weight: bold; text-align: center;")
                elif "min/sem" in col and col != "TOTAL min/sem":
                    styles.append("background-color: #d9d9d9; color: black; text-align: center;")
                elif col == "TOTAL min/sem":
                    if row["CAPACIDAD PRODUCTIVA"] == "Cuello de botella":
                        styles.append("background-color: #fca5a5; color: #991b1b; font-weight: bold; text-align: center;")
                    else:
                        styles.append("background-color: #93c5fd; color: #1e3a8a; font-weight: bold; text-align: center;")
                elif col == "CAPACIDAD PRODUCTIVA":
                    if row["CAPACIDAD PRODUCTIVA"] == "Cuello de botella":
                        styles.append("background-color: #fee2e2; color: #dc2626; font-weight: bold; text-align: center;")
                    else:
                        styles.append("background-color: #e5e7eb; color: #374151; text-align: center;")
                else:
                    styles.append("background-color: white; color: black; text-align: center;")
            return styles
            
        st.dataframe(df_res.style.apply(style_capacidad_planta, axis=1).format(precision=0), use_container_width=True, hide_index=True)
        
        # Params display table
        st.markdown("<br>", unsafe_allow_html=True)
        c_p1, c_p2, c_p3 = st.columns([1, 1, 2])
        with c_p3:
            df_glob = pd.DataFrame({
                "Parámetro": ["Jornada semanal (h/sem)", "Traslación min-hora (min/h)", "Equivalente minutos (min)"],
                "Valor": [jornada, 60, capacidad_disp_min]
            })
            st.dataframe(
                df_glob.style.apply(lambda row: ["background-color: #d9d9d9; color: black; font-weight: bold; text-align: right;", "background-color: white; color: black; text-align: center;"], axis=1).format({"Valor": "{:.0f}"}),
                use_container_width=True, hide_index=True
            )

    except Exception as e:
        st.error(f"SE HA PRODUCIDO UN ERROR: {e}")
