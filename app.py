import streamlit as st

st.set_page_config(
    page_title="Ejercicios Dirección de Producción",
    page_icon="🧊", # page_icon requires an emoji or image url, I'll use a neutral one or just text. Actually, string "DP" is supported? No, "random" or an emoji. I'll just use "▪" or remove page_icon.
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Premium CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Hide sidebar completely on landing page ── */
section[data-testid="stSidebar"],
div[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ── Header ── */
.main-header {
    text-align: center;
    padding: 55px 40px 45px 40px;
    background-color: #1e3a5f;
    border-radius: 24px;
    margin-bottom: 36px;
    box-shadow: 0 20px 60px rgba(15, 23, 42, 0.15);
}
.main-header h1 {
    color: #fff; font-size: 2.8rem; font-weight: 800; text-transform: uppercase;
    margin: 0 0 12px 0; letter-spacing: -1px;
    line-height: 1.15;
}
.main-header .subtitle {
    color: #93c5fd; font-size: 1.1rem; font-weight: 400;
    margin: 0 auto; max-width: 620px;
    line-height: 1.6;
}

/* ── Section ── */
.idx-title {
    font-size: 1.35rem; font-weight: 700; margin-bottom: 4px; text-transform: uppercase;
}
.idx-subtitle {
    font-size: 0.92rem; margin-bottom: 20px;
}

/* ── Card containers ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    border: 1px solid #e2e8f0 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 14px rgba(0,0,0,0.04) !important;
    background-color: #ffffff;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 10px 36px rgba(0,0,0,0.10) !important;
}

/* ── Card content ── */
.card-badge {
    display: inline-block; color: #fff;
    font-size: 0.7rem; font-weight: 700;
    padding: 3px 12px; border-radius: 16px;
    letter-spacing: 0.6px; text-transform: uppercase;
    margin-bottom: 8px;
}
.card-title {
    font-size: 1.12rem; font-weight: 700; text-transform: uppercase;
    margin-bottom: 12px; line-height: 1.3;
}

/* ── Navigation buttons ── */
.stButton > button {
    background-color: #e2e8f0 !important;
    color: #1e293b !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: 0.85rem !important; padding: 6px 0 !important;
    transition: all 0.25s ease !important;
    margin-bottom: 4px !important;
}
.stButton > button:hover {
    background-color: #cbd5e1 !important;
}

/* ── Footer ── */
.footer-bar {
    text-align: center; padding: 24px 0;
    color: #94a3b8; font-size: 0.82rem; margin-top: 8px;
    text-transform: uppercase; font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>EJERCICIOS DIRECCIÓN DE PRODUCCIÓN</h1>
    <p class="subtitle">PLATAFORMA INTERACTIVA DE CÁLCULO PARA TODOS LOS TEMAS DEL CURSO.<br>
    HAZ CLIC EN UN EJERCICIO PARA ACCEDER DIRECTAMENTE.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="idx-title">ÍNDICE DE TEMAS Y EJERCICIOS</div>'
    '<div class="idx-subtitle">Selecciona un ejercicio concreto para comenzar</div>',
    unsafe_allow_html=True,
)

# ── Topics ───────────────────────────────────────────────────────────────────
topics = [
    {
        "num": "TEMA 1", 
        "title": "INTRODUCCIÓN SISTEMAS PRODUCTIVOS",
        "accent": "#1e3a8a",
        "page": "pages/1_Punto_Equilibrio.py",
        "exercises": [
            "PUNTO DE EQUILIBRIO MULTIPRODUCTO",
            "PUNTO DE EQUILIBRIO UN PRODUCTO",
        ],
    },
    {
        "num": "TEMA 2", 
        "title": "GESTIÓN DE STOCKS",
        "accent": "#b45309",
        "page": "pages/2_Gestion_Stocks.py",
        "exercises": ["MODELO EOQ", "MODELO ABC"],
    },
    {
        "num": "TEMA 4", 
        "title": "PREVISIÓN DE LA DEMANDA",
        "accent": "#047857",
        "page": "pages/4_Prevision_Demanda.py",
        "exercises": [
            "ALISADO SIMPLE / DOBLE / TRIPLE",
            "MEDIA MÓVIL",
            "MEDIA MÓVIL PONDERADA",
        ],
    },
    {
        "num": "TEMA 5",
        "title": "PLANIFICACIÓN DE VENTAS",
        "accent": "#1d4ed8",
        "page": "pages/5_Planificacion_Ventas.py",
        "exercises": ["RED AON", "RED AOA", "DIAGRAMA DE GANTT"],
    },
    {
        "num": "TEMA 6", 
        "title": "SISTEMAS MRP Y MPS",
        "accent": "#be185d",
        "page": "pages/6_MRP_MPS.py",
        "exercises": ["MPS", "BOM", "MRP"],
    },
    {
        "num": "TEMA 7", 
        "title": "CONTROL DE PRODUCCIÓN",
        "accent": "#6d28d9",
        "page": "pages/7_Control_Produccion.py",
        "exercises": [
            "FIFO", "SPT", "EDD", "LPT", "RESUMEN COMPARATIVO"
        ],
    },
    {
        "num": "TEMA 8", 
        "title": "LEAN MANUFACTURING",
        "accent": "#b91c1c",
        "page": "pages/8_Lean_Manufacturing.py",
        "exercises": [
            "TAKT TIME Y TIEMPO DE CICLO",
            "SIMPLEX 2 VARIABLES",
            "CAPACIDAD Y CUELLOS DE BOTELLA",
        ],
    },
]

# ── Card grid ────────────────────────────────────────────────────────────────
for row_start in range(0, len(topics), 2):
    row = topics[row_start : row_start + 2]
    cols = st.columns(2)
    for i, topic in enumerate(row):
        with cols[i]:
            with st.container(border=True):
                st.markdown(
                    f'<span class="card-badge" style="background:{topic["accent"]}">'
                    f'{topic["num"]}</span>'
                    f'<div class="card-title">{topic["title"]}</div>',
                    unsafe_allow_html=True,
                )
                
                # Render a button for each exact exercise
                for idx_ex, ex_name in enumerate(topic["exercises"]):
                    if st.button(f"➔ {ex_name}", key=f"nav_{topic['num']}_{idx_ex}", use_container_width=True):
                        st.session_state["active_ejercicio"] = ex_name
                        st.switch_page(topic["page"])

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer-bar">DIRECCIÓN DE PRODUCCIÓN</div>',
    unsafe_allow_html=True,
)