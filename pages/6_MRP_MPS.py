import streamlit as st
import pandas as pd
import numpy as np
import math
from collections import defaultdict, deque

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="MRP y MPS", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.page-header { text-align: center; padding: 25px 20px; background-color: #be185d; color: white; border-radius: 10px; margin-bottom: 20px; font-weight: bold; }
.page-header h1 { color: #fff; font-size: 2.5rem; margin: 0; font-weight: 800; text-transform: uppercase; }
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
/* Fix input legibility when forcing white backgrounds */
[data-baseweb="input"], [data-baseweb="select"], [data-baseweb="radio"] { background-color: #ffffff !important; }
[data-baseweb="input"] input, [data-baseweb="select"] span { color: #1f1f1f !important; }
</style>
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

default_idx = 0
if "active_ejercicio" in st.session_state:
    if "BOM" in st.session_state["active_ejercicio"]:
        default_idx = 1
    elif "MRP" in st.session_state["active_ejercicio"]:
        default_idx = 2

modo = st.radio(
    "SELECCIONA EL EJERCICIO",
    ["MPS", "BOM", "MRP"],
    index=default_idx, horizontal=True, label_visibility="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# 6.1 MPS
# ══════════════════════════════════════════════════════════════════════════════
if modo == "MPS":
    st.markdown('<div class="page-header"><h1>MPS - PLAN MAESTRO DE PRODUCCIÓN</h1></div>', unsafe_allow_html=True)
    
    if "df_inputs_mps" not in st.session_state:
        st.session_state.df_inputs_mps = pd.DataFrame({
            "Parámetros": ["Previsión demanda (ud)", "Tamaño pedido (ud)"],
            "1": [800, 1200], "2": [700, 500], "3": [1000, 300], "4": [1000, 200],
            "5": [1600, 100], "6": [1500, 0], "7": [2000, 0], "8": [2000, 0]
        })
    if "mps_inv_ini" not in st.session_state:
        st.session_state.mps_inv_ini = 1200
    if "mps_lote" not in st.session_state:
        st.session_state.mps_lote = 1800
        
    col1, col2 = st.columns([1, 3])
    with col1:
        st.session_state.mps_inv_ini = st.number_input("Inventario inicial (ud)", value=st.session_state.mps_inv_ini, step=100)
        st.session_state.mps_lote = st.number_input("Tamaño lote prod (ud)", value=st.session_state.mps_lote, step=100)
    
    st.markdown("**DATOS DE ENTRADA (EDITABLES)**")
    
    # Button to add or remove a week (column)
    c_add, c_rm, c_space = st.columns([1, 1, 3])
    with c_add:
        if st.button("+ AÑADIR SEMANA", key="btn_add_sem_mps", use_container_width=True):
            n_cols = len(st.session_state.df_inputs_mps.columns)
            st.session_state.df_inputs_mps[str(n_cols)] = 0
            st.rerun()
    with c_rm:
        if st.button("- ELIMINAR SEMANA", key="btn_rm_sem_mps", use_container_width=True):
            if len(st.session_state.df_inputs_mps.columns) > 2: # Keep at least Parámetros and week 1
                last_col = st.session_state.df_inputs_mps.columns[-1]
                st.session_state.df_inputs_mps.drop(columns=[last_col], inplace=True)
                st.rerun()

    edited_inputs = st.data_editor(
        st.session_state.df_inputs_mps,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={"Parámetros": st.column_config.TextColumn("Parámetros", disabled=False)}
    )
    
    if st.button("CALCULAR MPS", type="primary"):
        st.session_state.df_inputs_mps = edited_inputs
        st.markdown("### RESOLUCIÓN")
        
        # Calculate dynamic number of periods
        n_periods = len(edited_inputs.columns) - 1
        
        # Find rows
        row_prev = edited_inputs[edited_inputs["Parámetros"] == "Previsión demanda (ud)"]
        row_ped = edited_inputs[edited_inputs["Parámetros"] == "Tamaño pedido (ud)"]
        
        prev_dem = row_prev.iloc[0, 1:].fillna(0).astype(int).values if not row_prev.empty else np.zeros(n_periods, dtype=int)
        pedidos = row_ped.iloc[0, 1:].fillna(0).astype(int).values if not row_ped.empty else np.zeros(n_periods, dtype=int)
        
        inv_ini_arr = np.zeros(n_periods, dtype=int)
        mps_arr = np.zeros(n_periods, dtype=int)
        inv_fin_arr = np.zeros(n_periods, dtype=int)
        
        curr_inv = int(st.session_state.mps_inv_ini)
        lote_prod = int(st.session_state.mps_lote)
        
        for t in range(n_periods):
            inv_ini_arr[t] = curr_inv
            max_dem = max(prev_dem[t], pedidos[t])
            
            if curr_inv - max_dem < 0:
                net_need = max_dem - curr_inv
                if lote_prod == 0:
                    mps_arr[t] = net_need
                else:
                    mps_arr[t] = math.ceil(net_need / lote_prod) * lote_prod
            else:
                mps_arr[t] = 0
                
            inv_fin_arr[t] = curr_inv + mps_arr[t] - max_dem
            curr_inv = inv_fin_arr[t]
            
        res_dict = {
            "Parámetros": [
                "Inventario inicial (ud)",
                "Previsión demanda (ud)",
                "Tamaño pedido (ud)",
                "MPS (ud)",
                "Inventario final (ud)"
            ]
        }
        for t in range(n_periods):
            cname = edited_inputs.columns[t+1]
            res_dict[cname] = [
                inv_ini_arr[t], prev_dem[t], pedidos[t], mps_arr[t], inv_fin_arr[t]
            ]
            
        df_res = pd.DataFrame(res_dict)
        
        def style_mps(row):
            styles = []
            for col in df_res.columns:
                if col == "Parámetros":
                    if row["Parámetros"] == "MPS (ud)":
                        styles.append("background-color: #b3d9ff; color: #0066cc; font-weight: bold;")
                    else:
                        styles.append("background-color: #0066cc; color: white; font-weight: bold;")
                else:
                    if row["Parámetros"] in ["Inventario inicial (ud)", "Inventario final (ud)"]:
                        styles.append("background-color: #d9d9d9; color: black; text-align: center;")
                    elif row["Parámetros"] == "MPS (ud)":
                        val = row[col]
                        color = "#0066cc" if val > 0 else "#99c2ff"
                        styles.append(f"background-color: #b3d9ff; color: {color}; font-weight: bold; text-align: center;")
                    else:
                        styles.append("background-color: white; color: black; text-align: center;")
            return styles
        
        st.dataframe(df_res.style.apply(style_mps, axis=1), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# 6.2 BOM
# ══════════════════════════════════════════════════════════════════════════════
elif modo == "BOM":
    st.markdown('<div class="page-header"><h1>BOM - LISTA DE MATERIALES</h1></div>', unsafe_allow_html=True)
    
    if "df_mpc" not in st.session_state:
        st.session_state.df_mpc = pd.DataFrame({
            "Elemento": ["Producto 1", "Producto 2"],
            "Conjunto 1": [1, 1], "Conjunto 2": [1, 2]
        })
    if "df_mzc" not in st.session_state:
        st.session_state.df_mzc = pd.DataFrame({
            "Elemento": ["Pieza 1", "Pieza 2", "Pieza 3", "Pieza 4"],
            "Conjunto 1": [2, 5, 20, 0], "Conjunto 2": [1, 4, 0, 16]
        })
    if "df_dem_bom" not in st.session_state:
        st.session_state.df_dem_bom = pd.DataFrame({
            "Producto": ["Producto 1", "Producto 2"], "Cantidad": [10, 7]
        })

    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.markdown("**MATRIZ DE PRODUCTOS A CONJUNTOS (M_PC)**")
        c_add, c_rm = st.columns(2)
        with c_add:
            if st.button("+ AÑADIR CONJUNTO", key="add_conj", use_container_width=True):
                n = len(st.session_state.df_mpc.columns)
                cname = f"Conjunto {n}"
                st.session_state.df_mpc[cname] = 0
                st.session_state.df_mzc[cname] = 0
                st.rerun()
        with c_rm:
            if st.button("- ELIMINAR CONJUNTO", key="rm_conj", use_container_width=True):
                if len(st.session_state.df_mpc.columns) > 2: # Keep at least Elemento and Conjunto 1
                    last_col = st.session_state.df_mpc.columns[-1]
                    st.session_state.df_mpc.drop(columns=[last_col], inplace=True)
                    st.session_state.df_mzc.drop(columns=[last_col], inplace=True)
                    st.rerun()
            
        ed_mpc = st.data_editor(st.session_state.df_mpc, use_container_width=True, hide_index=True, num_rows="dynamic")
        
        st.markdown("**MATRIZ DE PIEZAS A CONJUNTOS (M_ZC)**")
        ed_mzc = st.data_editor(st.session_state.df_mzc, use_container_width=True, hide_index=True, num_rows="dynamic")
        
    with col_m2:
        st.markdown("**DEMANDA DE PRODUCTOS (VECTOR D)**")
        ed_dem = st.data_editor(st.session_state.df_dem_bom, use_container_width=True, hide_index=True, num_rows="dynamic")
        
    if st.button("CALCULAR MATRICES", type="primary"):
        st.session_state.df_mpc = ed_mpc
        st.session_state.df_mzc = ed_mzc
        st.session_state.df_dem_bom = ed_dem
        st.markdown("### RESOLUCIÓN")
        
        try:
            # Limpiar filas vacías
            _mpc = ed_mpc.dropna(subset=["Elemento"])
            _mzc = ed_mzc.dropna(subset=["Elemento"])
            _dem = ed_dem.dropna(subset=["Producto"])
            
            # Productos
            productos = _mpc["Elemento"].astype(str).values
            conjuntos = _mpc.columns[1:].values
            piezas = _mzc["Elemento"].astype(str).values
            
            # (Conjuntos x Productos)
            M_PC = _mpc.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int).values.T  
            
            # (Piezas x Conjuntos)
            M_ZC = _mzc.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int).values    
            
            # Map demand to the exact products in M_PC
            demand_dict = dict(zip(_dem["Producto"].astype(str), pd.to_numeric(_dem["Cantidad"], errors='coerce').fillna(0)))
            D_arr = np.array([demand_dict.get(p, 0) for p in productos]).reshape(-1, 1)
            
            # 1. Conjuntos precisos = M_PC x D
            C_prec = np.dot(M_PC, D_arr)
            df_c_prec = pd.DataFrame({"Conjuntos": conjuntos, "Cantidad": C_prec.flatten()})
            
            # 2. Matriz básica = M_ZC x M_PC
            M_Basica = np.dot(M_ZC, M_PC)
            df_m_basica = pd.DataFrame(M_Basica, columns=productos)
            df_m_basica.insert(0, "Piezas", piezas)
            
            # 3. Piezas precisas = M_Basica x D
            P_prec = np.dot(M_Basica, D_arr)
            df_p_prec = pd.DataFrame({"Piezas": piezas, "Cantidad": P_prec.flatten()})
            
            def style_res(row):
                styles = []
                for col in row.index:
                    if col in ["Conjuntos", "Piezas"]:
                        styles.append("background-color: #0066cc; color: white; font-weight: bold;")
                    else:
                        styles.append("background-color: #f8fafc; color: black; text-align: center;")
                return styles

            cr1, cr2, cr3 = st.columns(3)
            with cr1:
                st.markdown("**CONJUNTOS PRECISOS**")
                st.dataframe(df_c_prec.style.apply(style_res, axis=1), hide_index=True, use_container_width=True)
            with cr2:
                st.markdown("**MATRIZ BÁSICA**")
                st.dataframe(df_m_basica.style.apply(style_res, axis=1), hide_index=True, use_container_width=True)
            with cr3:
                st.markdown("**PIEZAS PRECISAS**")
                st.dataframe(df_p_prec.style.apply(style_res, axis=1), hide_index=True, use_container_width=True)
                
        except Exception as e:
            st.error(f"ERROR EN EL CÁLCULO: VERIFICA QUE LAS TABLAS NO TENGAN CELDAS VACÍAS. ({e})")


# ══════════════════════════════════════════════════════════════════════════════
# 6.3 MRP
# ══════════════════════════════════════════════════════════════════════════════
elif modo == "MRP":
    st.markdown('<div class="page-header"><h1>MRP - PLANIFICACIÓN REQUERIMIENTOS</h1></div>', unsafe_allow_html=True)
    
    if "df_mps_maestra" not in st.session_state:
        st.session_state.df_mps_maestra = pd.DataFrame({
            "Elemento": ["A", "B", "C", "D"],
            "Tiempo espera (sem)": [1, 1, 1, 2],
            "Tamaño lote (ud)": [0, 500, 550, 350],
            "Stock (ud)": [75, 40, 50, 110],
            "Recepciones programadas (ud)": [50, 0, 0, 200],
            "Rec. Prog. Período": [1, 0, 0, 2],
            "SS (ud)": [0, 10, 0, 0]
        })
        
    if "df_req_a" not in st.session_state:
        st.session_state.df_req_a = pd.DataFrame({
            "1": [0], "2": [100], "3": [0], "4": [60], 
            "5": [50], "6": [0], "7": [40], "8": [55]
        })
        st.session_state.df_req_a.insert(0, "Parámetros", ["Req brutos A"])
        
    if "df_bom_rel" not in st.session_state:
        st.session_state.df_bom_rel = pd.DataFrame({
            "Padre": ["A", "A", "C", "C"],
            "Hijo": ["B", "C", "B", "D"],
            "Cantidad": [1, 2, 3, 2]
        })

    st.markdown("### TABLA MRP MAESTRA")
    ed_mps = st.data_editor(st.session_state.df_mps_maestra, use_container_width=True, hide_index=True, num_rows="dynamic")
    
    col_req, col_bom = st.columns([2, 1])
    
    with col_req:
        st.markdown("### REQUERIMIENTOS BRUTOS INICIALES (PRODUCTO RAÍZ)")
        if st.button("+ AÑADIR SEMANA (COLUMNA)", key="add_sem_mrp"):
            n = len(st.session_state.df_req_a.columns)
            st.session_state.df_req_a[str(n)] = 0
            st.rerun()
            
        ed_req_a = st.data_editor(st.session_state.df_req_a, use_container_width=True, hide_index=True, num_rows="dynamic")
        
    with col_bom:
        st.markdown("### ÁRBOL BOM (DEPENDENCIAS)")
        ed_bom = st.data_editor(st.session_state.df_bom_rel, use_container_width=True, hide_index=True, num_rows="dynamic")
        
    if st.button("CALCULAR MRP MULTI-NIVEL", type="primary"):
        st.session_state.df_mps_maestra = ed_mps
        st.session_state.df_req_a = ed_req_a
        st.session_state.df_bom_rel = ed_bom
        st.markdown("### RESOLUCIÓN MRP")
        
        try:
            n_periods = len(ed_req_a.columns) - 1
            
            mrp_data = {}
            for _, row in ed_mps.iterrows():
                item = str(row["Elemento"]).strip()
                if not item: continue
                mrp_data[item] = {
                    "lt": int(row["Tiempo espera (sem)"]),
                    "lote": int(row["Tamaño lote (ud)"]),
                    "inv_ini": int(row["Stock (ud)"]),
                    "ss": int(row["SS (ud)"]),
                    "rec_prog_qty": int(row["Recepciones programadas (ud)"]),
                    "rec_prog_t": int(row["Rec. Prog. Período"]),
                    "req_brutos": [0]*n_periods,
                    "rec_prog": [0]*n_periods,
                    "proy_disp": [0]*n_periods,
                    "req_netos": [0]*n_periods,
                    "lib_orden": [0]*n_periods
                }
                
                if mrp_data[item]["rec_prog_qty"] > 0 and 1 <= mrp_data[item]["rec_prog_t"] <= n_periods:
                    mrp_data[item]["rec_prog"][mrp_data[item]["rec_prog_t"] - 1] = mrp_data[item]["rec_prog_qty"]
            
            # Find the root elements from df_req_a
            for idx, row in ed_req_a.iterrows():
                # Expected "Req brutos X"
                param_name = str(row["Parámetros"]).strip()
                item = param_name.split()[-1] if " " in param_name else param_name
                if item in mrp_data:
                    mrp_data[item]["req_brutos"] = list(row.iloc[1:].fillna(0).astype(int).values)
                
            # Topological sort
            adj = defaultdict(list)
            in_degree = defaultdict(int)
            elements = list(mrp_data.keys())
            
            for e in elements:
                in_degree[e] = 0
                
            for _, rel in ed_bom.iterrows():
                p = str(rel["Padre"]).strip()
                h = str(rel["Hijo"]).strip()
                if p in elements and h in elements:
                    adj[p].append((h, int(rel["Cantidad"])))
                    in_degree[h] += 1
                    
            queue = deque([e for e in elements if in_degree[e] == 0])
            elements_order = []
            
            while queue:
                curr = queue.popleft()
                elements_order.append(curr)
                for hijo, qty in adj[curr]:
                    in_degree[hijo] -= 1
                    if in_degree[hijo] == 0:
                        queue.append(hijo)
            
            # Fallback if there's a cycle or disconnected
            for e in elements:
                if e not in elements_order:
                    elements_order.append(e)
            
            # Calculation Engine
            for item in elements_order:
                d = mrp_data[item]
                curr_inv = d["inv_ini"]
                
                for t in range(n_periods):
                    gr = d["req_brutos"][t]
                    sr = d["rec_prog"][t]
                    
                    disp = curr_inv + sr - gr
                    
                    if disp < d["ss"]:
                        nn = d["ss"] - disp
                        d["req_netos"][t] = nn
                        
                        if d["lote"] == 0:
                            plan_rec = nn
                        else:
                            plan_rec = math.ceil(nn / d["lote"]) * d["lote"]
                            
                        disp += plan_rec
                        
                        rel_t = t - d["lt"]
                        if 0 <= rel_t < n_periods:
                            d["lib_orden"][rel_t] += plan_rec
                    else:
                        d["req_netos"][t] = 0
                    
                    d["proy_disp"][t] = disp
                    curr_inv = disp
                    
                # Propagate to children
                for hijo, qty in adj[item]:
                    for t in range(n_periods):
                        mrp_data[hijo]["req_brutos"][t] += d["lib_orden"][t] * qty
                                
            # Render Results
            def render_mrp_table(item_name, data):
                res_dict = {"Parámetros": ["Req brutos", "Rec prog", "Proy disp", "Req netos", "Lib orden"]}
                
                # Fetch original column names for the periods
                col_names = ed_req_a.columns[1:] 
                for t in range(n_periods):
                    res_dict[col_names[t]] = [
                        data["req_brutos"][t], data["rec_prog"][t], data["proy_disp"][t], 
                        data["req_netos"][t], data["lib_orden"][t]
                    ]
                
                df = pd.DataFrame(res_dict)
                
                def style_mrp(row):
                    styles = []
                    for col in df.columns:
                        if col == "Parámetros":
                            styles.append("background-color: #0066cc; color: white; font-weight: bold;")
                        else:
                            val = row[col]
                            if row["Parámetros"] == "Proy disp":
                                styles.append("background-color: #d9d9d9; color: black; text-align: center;")
                            elif val > 0:
                                styles.append("background-color: white; color: black; font-weight: bold; text-align: center;")
                            else:
                                styles.append("background-color: white; color: transparent; text-align: center;") 
                    return styles
                
                st.markdown(f"#### ELEMENTO: {item_name}")
                st.dataframe(df.style.apply(style_mrp, axis=1), use_container_width=True, hide_index=True)

            cr_a, cr_b = st.columns(2)
            
            # Try to place sequentially in 2 columns
            for i, item in enumerate(elements_order):
                if i % 2 == 0:
                    with cr_a: render_mrp_table(item, mrp_data[item])
                else:
                    with cr_b: render_mrp_table(item, mrp_data[item])
                    
        except Exception as e:
            st.error(f"ERROR EN EL CÁLCULO: VERIFICA QUE LAS TABLAS SEAN CONSISTENTES. DETALLES: {e}")
