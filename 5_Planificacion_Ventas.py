import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import graphviz
from collections import defaultdict, deque

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Planificación de Ventas", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stMetricValue"] { color: #1f1f1f !important; }
[data-testid="stMetricLabel"] { color: #31333F !important; }
.stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.page-header { text-align: center; padding: 35px 30px; background-color: #1d4ed8; border-radius: 20px; margin-bottom: 32px; box-shadow: 0 10px 40px rgba(0,0,0,0.25); }
.page-header h1 { color: #fff; font-size: 2.2rem; font-weight: 800; margin: 0 0 8px 0; text-transform: uppercase; }
.page-header p { color: #93c5fd; font-size: 1rem; margin: 0; }
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
    <h1>TEMA 5 · PLANIFICACIÓN DE VENTAS Y OPERACIONES</h1>
    <p>Redes AON, AOA y Diagramas de Gantt</p>
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

def parse_predecessors(pred_str):
    """Parse predecessor string, splitting by ; or , and stripping whitespace."""
    if pd.isna(pred_str) or str(pred_str).strip() == "" or str(pred_str).strip() == "-":
        return []
    return [p.strip() for p in str(pred_str).replace(",", ";").split(";") if p.strip()]


def topological_sort(activities, predecessors):
    """Return activities in topological order. Raises ValueError on cycles."""
    in_degree = {a: 0 for a in activities}
    adj = defaultdict(list)
    for a in activities:
        for p in predecessors.get(a, []):
            if p in in_degree:
                adj[p].append(a)
                in_degree[a] += 1

    queue = deque([a for a in activities if in_degree[a] == 0])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(activities):
        raise ValueError("Se detectó un ciclo en las dependencias. Revisa las predecesoras.")
    return order


def compute_cpm(df):
    """Compute Critical Path Method. Returns dict with all results."""
    activities = list(df["Actividad"])
    durations = dict(zip(df["Actividad"], df["Duración"]))
    predecessors = {}
    for _, row in df.iterrows():
        predecessors[row["Actividad"]] = parse_predecessors(row["Predecesoras"])

    # Validate predecessors
    all_acts = set(activities)
    for act, preds in predecessors.items():
        for p in preds:
            if p not in all_acts:
                raise ValueError(f"Actividad '{act}' tiene predecesora '{p}' que no existe.")

    order = topological_sort(activities, predecessors)

    # Build successors
    successors = defaultdict(list)
    for a in activities:
        for p in predecessors.get(a, []):
            successors[p].append(a)

    # Forward pass
    ES = {}
    EF = {}
    for a in order:
        preds = predecessors.get(a, [])
        if not preds:
            ES[a] = 0
        else:
            ES[a] = max(EF[p] for p in preds)
        EF[a] = ES[a] + durations[a]

    project_duration = max(EF.values()) if EF else 0

    # Backward pass
    LS = {}
    LF = {}
    for a in reversed(order):
        succs = successors.get(a, [])
        if not succs:
            LF[a] = project_duration
        else:
            LF[a] = min(LS[s] for s in succs)
        LS[a] = LF[a] - durations[a]

    # Slack and critical path
    slack = {a: LS[a] - ES[a] for a in activities}
    critical = [a for a in order if slack[a] == 0]

    return {
        "activities": activities,
        "order": order,
        "durations": durations,
        "predecessors": predecessors,
        "successors": successors,
        "ES": ES, "EF": EF, "LS": LS, "LF": LF,
        "slack": slack,
        "critical": critical,
        "project_duration": project_duration,
    }


def build_results_table(cpm):
    """Build a results DataFrame from CPM results."""
    rows = []
    for a in cpm["order"]:
        rows.append({
            "Actividad": a,
            "Duración": cpm["durations"][a],
            "ES": cpm["ES"][a],
            "EF": cpm["EF"][a],
            "LS": cpm["LS"][a],
            "LF": cpm["LF"][a],
            "Holgura": cpm["slack"][a],
            "Crítica": "✓" if cpm["slack"][a] == 0 else "✗",
        })
    return pd.DataFrame(rows)


def assign_layers(order, predecessors):
    """Assign each activity to a layer for visualization (longest path from start)."""
    layer = {}
    for a in order:
        preds = predecessors.get(a, [])
        if not preds:
            layer[a] = 0
        else:
            layer[a] = max(layer[p] for p in preds) + 1
    return layer


def draw_aon_network(cpm):
    """Draw AON network using graphviz (Nodes are activities with ES/EF/LS/LF grid)."""
    dot = graphviz.Digraph(engine='dot')
    dot.attr(rankdir='LR', size='10,6')
    
    order = cpm["order"]
    predecessors = cpm["predecessors"]
    critical_set = set(cpm["critical"])
    
    # Identify start and end activities
    start_acts = [a for a in order if not predecessors.get(a, [])]
    
    successors = defaultdict(list)
    for a in order:
        for p in predecessors.get(a, []):
            successors[p].append(a)
    end_acts = [a for a in order if not successors.get(a, [])]
    
    project_duration = cpm["project_duration"]

    # Draw INICIO node
    color_inicio = "#ef4444" if any(a in critical_set for a in start_acts) else "black"
    inicio_label = f'''<
    <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" COLOR="{color_inicio}">
      <TR><TD>0</TD><TD>0</TD></TR>
      <TR><TD COLSPAN="2">INICIO</TD></TR>
      <TR><TD>0</TD><TD>0</TD></TR>
    </TABLE>>'''
    dot.node("INICIO", label=inicio_label, shape="plaintext")

    # Draw FINAL node
    color_final = "#ef4444" if any(a in critical_set for a in end_acts) else "black"
    final_label = f'''<
    <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" COLOR="{color_final}">
      <TR><TD>{project_duration}</TD><TD>{project_duration}</TD></TR>
      <TR><TD COLSPAN="2">FINAL</TD></TR>
      <TR><TD>{project_duration}</TD><TD>{project_duration}</TD></TR>
    </TABLE>>'''
    dot.node("FINAL", label=final_label, shape="plaintext")

    # Draw nodes with ES, EF, LS, LF
    for a in order:
        is_crit = a in critical_set
        color = "#ef4444" if is_crit else "black"
        
        es = cpm['ES'][a]
        ef = cpm['EF'][a]
        ls = cpm['LS'][a]
        lf = cpm['LF'][a]
        dur = cpm['durations'][a]
        
        label = f'''<
        <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" COLOR="{color}">
          <TR><TD>{es}</TD><TD>{ef}</TD></TR>
          <TR><TD COLSPAN="2">{a} ({dur})</TD></TR>
          <TR><TD>{ls}</TD><TD>{lf}</TD></TR>
        </TABLE>>'''
        
        dot.node(a, label=label, shape="plaintext")

    # Draw edges from INICIO
    for a in start_acts:
        is_crit = a in critical_set
        color = "#ef4444" if is_crit else "black"
        penwidth = "2.0" if is_crit else "1.0"
        dot.edge("INICIO", a, color=color, penwidth=penwidth)

    # Draw standard edges
    for a in order:
        for p in predecessors.get(a, []):
            is_crit_edge = p in critical_set and a in critical_set
            color = "#ef4444" if is_crit_edge else "black"
            penwidth = "2.0" if is_crit_edge else "1.0"
            dot.edge(p, a, color=color, penwidth=penwidth)

    # Draw edges to FINAL
    for a in end_acts:
        is_crit = a in critical_set
        color = "#ef4444" if is_crit else "black"
        penwidth = "2.0" if is_crit else "1.0"
        dot.edge(a, "FINAL", color=color, penwidth=penwidth)
            
    return dot


def draw_aoa_network(cpm):
    """Draw AOA network using graphviz (Nodes are events, Arcs are activities)."""
    order = cpm["order"]
    predecessors = cpm["predecessors"]
    critical_set = set(cpm["critical"])
    successors = cpm["successors"]

    # 1. Identify unique predecessor sets
    unique_preds = set()
    for a in order:
        preds = tuple(sorted(predecessors.get(a, [])))
        unique_preds.add(preds)

    # 2. Create nodes mapping
    act_start_node = {}
    act_end_node = {}
    
    # Assign end nodes for all activities
    for a in order:
        act_end_node[a] = f"End_{a}"
        
    # Assign start nodes based on predecessor sets
    for a in order:
        preds = tuple(sorted(predecessors.get(a, [])))
        if not preds:
            act_start_node[a] = "START"
        elif len(preds) == 1:
            act_start_node[a] = f"End_{preds[0]}"
        else:
            act_start_node[a] = f"Merge_{'_'.join(preds)}"
            
    # Terminate project: Activities with no successors merge to FINAL
    end_acts = [a for a in order if not successors.get(a, [])]
    for a in end_acts:
        act_end_node[a] = "FINAL"

    # 3. Collect all nodes and edges
    edges = []  # tuples of (u, v, label, is_crit)
    
    for a in order:
        u = act_start_node[a]
        v = act_end_node[a]
        is_crit = a in critical_set
        edges.append((u, v, a, is_crit))

    f_counter = 1
    for preds in unique_preds:
        if len(preds) > 1:
            v = f"Merge_{'_'.join(preds)}"
            for p in preds:
                u = act_end_node[p]
                if u != v:
                    # check if dummy is redundant (e.g. u is already connected to v)
                    edges.append((u, v, f"f{f_counter}", False))
                    f_counter += 1

    # 4. Topological sort of events to assign sequence numbers (1, 2, 3...)
    nodes = set()
    for u, v, label, is_crit in edges:
        nodes.add(u)
        nodes.add(v)
        
    adj = defaultdict(list)
    in_degree = {n: 0 for n in nodes}
    for u, v, label, is_crit in edges:
        adj[u].append(v)
        in_degree[v] += 1
        
    queue = deque([n for n in nodes if in_degree[n] == 0])
    sorted_nodes = []
    while queue:
        n = queue.popleft()
        sorted_nodes.append(n)
        for neighbor in adj[n]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
                
    for n in nodes:
        if n not in sorted_nodes:
            sorted_nodes.append(n)
            
    node_id = {n: i+1 for i, n in enumerate(sorted_nodes)}

    for a in order:
        act_start_node[a] = node_id[act_start_node[a]]
        act_end_node[a] = node_id[act_end_node[a]]
        
    id_edges = []
    for u, v, label, is_crit in edges:
        id_edges.append((node_id[u], node_id[v], label, is_crit))

    event_list = sorted(node_id.values())

    # 5. Calculate TE and TL for events
    TE = {i: 0 for i in event_list}
    for n in sorted_nodes:
        u_id = node_id[n]
        for v in adj[n]:
            v_id = node_id[v]
            weight = 0
            for eu, ev, elabel, ecrit in edges:
                if eu == n and ev == v:
                    w = cpm["durations"][elabel] if not elabel.startswith("f") else 0
                    if w > weight: weight = w
            TE[v_id] = max(TE[v_id], TE[u_id] + weight)

    TL = {i: cpm["project_duration"] for i in event_list}
    for n in reversed(sorted_nodes):
        u_id = node_id[n]
        for v in adj[n]:
            v_id = node_id[v]
            weight = 0
            for eu, ev, elabel, ecrit in edges:
                if eu == n and ev == v:
                    w = cpm["durations"][elabel] if not elabel.startswith("f") else 0
                    if w > weight: weight = w
            TL[u_id] = min(TL[u_id], TL[v_id] - weight)

    # 6. Graphviz visualization
    dot = graphviz.Digraph(engine='dot')
    dot.attr(rankdir='LR', size='10,6')

    for e in event_list:
        # Node is critical if TE == TL and it connects critical activities
        is_crit_event = (TE[e] == TL[e]) and any(
            ((id_edges[i][0] == e or id_edges[i][1] == e) and id_edges[i][3])
            for i in range(len(id_edges))
        )
        color = "#ef4444" if is_crit_event else "black"
        fontcolor = "#ef4444" if is_crit_event else "black"
        penwidth = "2.0" if is_crit_event else "1.0"
        
        te = TE[e]
        tl = TL[e]
        
        label = f"{{ {e} | {{ {te} | {tl} }} }}"
        dot.node(str(e), label=label, shape="Mrecord", color=color, fontcolor=fontcolor, penwidth=penwidth)

    for u, v, label, is_crit in id_edges:
        if label.startswith("f"):
            dot.edge(str(u), str(v), label=f"{label}\\n0", style="dashed", color="#9ca3af", fontcolor="#9ca3af")
        else:
            color = "#ef4444" if is_crit else "black"
            fontcolor = "#ef4444" if is_crit else "black"
            penwidth = "2.0" if is_crit else "1.0"
            edge_label = f"{label}\\n{cpm['durations'][label]}"
            dot.edge(str(u), str(v), label=edge_label, color=color, fontcolor=fontcolor, penwidth=penwidth)

    return dot


def draw_gantt(cpm):
    """Draw Gantt chart using plotly horizontal bars."""
    order = list(reversed(cpm["order"]))  # Reverse so A is on top
    critical_set = set(cpm["critical"])

    fig = go.Figure()

    # Slack bars (draw first so they appear behind)
    for a in order:
        if cpm["slack"][a] > 0:
            fig.add_trace(go.Bar(
                y=[a],
                x=[cpm["slack"][a]],
                base=[cpm["EF"][a]],
                orientation="h",
                marker=dict(color="rgba(59,130,246,0.15)", line=dict(color="#93c5fd", width=1)),
                name="Holgura",
                showlegend=a == next((act for act in order if cpm["slack"][act] > 0), None),
                hovertemplate=f"{a}: Holgura = {cpm['slack'][a]}<extra></extra>",
            ))

    # Activity bars
    added_crit_legend = False
    added_normal_legend = False
    for a in order:
        is_crit = a in critical_set
        color = "#ef4444" if is_crit else "#3b82f6"

        if is_crit and not added_crit_legend:
            show_legend = True
            added_crit_legend = True
            legend_name = "Crítica"
        elif not is_crit and not added_normal_legend:
            show_legend = True
            added_normal_legend = True
            legend_name = "No Crítica"
        else:
            show_legend = False
            legend_name = ""

        fig.add_trace(go.Bar(
            y=[a],
            x=[cpm["durations"][a]],
            base=[cpm["ES"][a]],
            orientation="h",
            marker=dict(color=color, line=dict(color="white", width=0.5)),
            name=legend_name,
            showlegend=show_legend,
            hovertemplate=f"{a}: ES={cpm['ES'][a]}, EF={cpm['EF'][a]}, Dur={cpm['durations'][a]}<extra></extra>",
            text=[f"{a} ({cpm['durations'][a]})"],
            textposition="inside",
            textfont=dict(color="white", size=12, family="Inter"),
        ))

    fig.update_layout(
        title="DIAGRAMA DE GANTT",
        xaxis=dict(title="TIEMPO (PERÍODOS)", range=[-0.5, cpm["project_duration"] + 1], showline=True, linewidth=2, linecolor='black', mirror=True),
        yaxis=dict(title="", showline=True, linewidth=2, linecolor='black', mirror=True),
        barmode="overlay",
        height=max(350, len(order) * 50 + 100),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=80, b=120),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e5e7eb")
    fig.update_yaxes(showgrid=False)
    return fig


# ── Default data ─────────────────────────────────────────────────────────────
default_data = pd.DataFrame({
    "Actividad": ["A", "B", "C", "D", "E", "F"],
    "Duración": [3, 4, 2, 5, 3, 2],
    "Predecesoras": ["", "", "A", "A;B", "C;D", "E"],
})

# ── Mode selection ───────────────────────────────────────────────────────────
default_idx = 0
if "active_ejercicio" in st.session_state:
    if "AOA" in st.session_state["active_ejercicio"]:
        default_idx = 1
    elif "GANTT" in st.session_state["active_ejercicio"]:
        default_idx = 2

modo = st.selectbox(
    "SELECCIONA EL TIPO DE VISUALIZACIÓN",
    ["RED AON (ACTIVITY ON NODE)", "RED AOA (ACTIVITY ON ARC)", "DIAGRAMA DE GANTT"],
    index=default_idx,
    key="modo_t5",
)

# ── Input data ───────────────────────────────────────────────────────────────
st.subheader("DATOS DE ACTIVIDADES")
st.caption("Introduce las actividades, duraciones y predecesoras. Usa `;` o `,` para separar múltiples predecesoras. Deja vacío si no tiene predecesoras.")

if "df_actividades_t5" not in st.session_state:
    st.session_state.df_actividades_t5 = default_data.copy()

edited_df = st.data_editor(
    st.session_state.df_actividades_t5,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_t5",
    column_config={
        "Actividad": st.column_config.TextColumn("Actividad", required=True),
        "Duración": st.column_config.NumberColumn("Duración", min_value=1, required=True),
        "Predecesoras": st.column_config.TextColumn("Predecesoras", help="Separar con ; o ,"),
    },
)

# ── Calculate ────────────────────────────────────────────────────────────────
if st.button("CALCULAR", type="primary", use_container_width=True):
    try:
        df = edited_df.copy()
        st.session_state.df_actividades_t5 = df.copy()

        # Validation
        df = df.dropna(subset=["Actividad", "Duración"])
        if df.empty:
            st.error("NO HAY ACTIVIDADES VÁLIDAS. AÑADE AL MENOS UNA ACTIVIDAD.")
            st.stop()

        df["Duración"] = df["Duración"].astype(int)
        df["Predecesoras"] = df["Predecesoras"].fillna("")

        # Check for duplicates
        if df["Actividad"].duplicated().any():
            st.error("HAY ACTIVIDADES DUPLICADAS. CADA ACTIVIDAD DEBE TENER UN NOMBRE ÚNICO.")
            st.stop()

        # Compute CPM
        cpm = compute_cpm(df)

        # ── Metrics ──────────────────────────────────────────────────────
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("DURACIÓN DEL PROYECTO", f"{cpm['project_duration']} períodos")
        with col2:
            st.metric("CAMINO CRÍTICO", " → ".join(cpm["critical"]))

        # ── Results table ────────────────────────────────────────────────
        st.subheader("TABLA DE RESULTADOS CPM")
        results_df = build_results_table(cpm)

        def style_results(row):
            styles = []
            for col in results_df.columns:
                if col == "Actividad":
                    styles.append("background-color: #0066cc; color: white; font-weight: bold;")
                elif row["Crítica"] == "✓":
                    styles.append("background-color: #fef2f2; color: #991b1b; font-weight: 600")
                else:
                    styles.append("background-color: #f8fafc; color: black;")
            return styles

        st.dataframe(
            results_df.style.apply(style_results, axis=1).format(precision=0, na_rep=""),
            use_container_width=True,
            hide_index=True,
        )

        # ── Visualization ────────────────────────────────────────────────
        st.subheader(f"{modo}")

        if modo == "RED AON (ACTIVITY ON NODE)":
            graph = draw_aon_network(cpm)
            st.graphviz_chart(graph)
        elif modo == "RED AOA (ACTIVITY ON ARC)":
            graph = draw_aoa_network(cpm)
            st.graphviz_chart(graph)
        else:
            fig = draw_gantt(cpm)
            st.plotly_chart(fig, use_container_width=True)

    except ValueError as ve:
        st.error(f"ERROR DE VALIDACIÓN: {ve}")
    except Exception as e:
        st.error(f"SE HA PRODUCIDO UN ERROR: {e}")
