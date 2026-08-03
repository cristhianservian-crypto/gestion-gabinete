import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from io import BytesIO
from datetime import datetime, date

# =========================================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Viceministerio de Mipymes | Control de Gestión",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# SISTEMA DE DISEÑO INSTITUCIONAL
# Paleta:  navy #0E2A47 · gold #C39B4E · ink #0B1524
#          fondo #F1F4F8 · líneas #E3E9F1
# Tipos:   Plus Jakarta Sans (títulos) + Inter (datos)
# =========================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
    --navy:#0E2A47;
    --navy-700:#153A5F;
    --ink:#0B1524;
    --gold:#C39B4E;
    --bg:#F1F4F8;
    --line:#E3E9F1;
    --muted:#64748B;
    --soft:#F8FAFC;
    --ok:#0F7B4F;
    --warn:#B45309;
    --danger:#B42318;
    --info:#1D4ED8;
    --radius:14px;
    --shadow:0 1px 2px rgba(11,21,36,.04), 0 8px 24px rgba(11,21,36,.06);
}

/* ---------- BASE ---------- */
.stApp{
    background:
        radial-gradient(1200px 420px at 12% -10%, rgba(14,42,71,.07), transparent 60%),
        var(--bg);
    font-family:'Inter', system-ui, -apple-system, sans-serif;
    color:var(--ink);
}
header[data-testid="stHeader"]{ background:transparent; }
[data-testid="stToolbar"]{ right:1rem; }
#MainMenu, footer{ visibility:hidden; }
.block-container{ padding-top:1.6rem; padding-bottom:3.5rem; max-width:1500px; }

h1,h2,h3,h4,h5,h6{ font-family:'Plus Jakarta Sans', sans-serif; color:var(--ink); letter-spacing:-.015em; }
hr{ border:none; border-top:1px solid var(--line); margin:1.4rem 0; }

/* ---------- BARRA INSTITUCIONAL ---------- */
.app-header{
    display:flex; align-items:center; justify-content:space-between; gap:24px; flex-wrap:wrap;
    background:linear-gradient(120deg,#0B2138 0%, #0E2A47 46%, #17456F 100%);
    border-radius:18px; padding:22px 26px; margin-bottom:22px;
    box-shadow:0 12px 30px rgba(11,21,36,.18);
    position:relative; overflow:hidden;
}
.app-header::after{
    content:""; position:absolute; inset:0;
    background:repeating-linear-gradient(115deg, rgba(255,255,255,.035) 0 2px, transparent 2px 22px);
    pointer-events:none;
}
.brand{ display:flex; align-items:center; gap:16px; z-index:1; }
.brand-mark{
    width:50px; height:50px; border-radius:13px; flex:none;
    display:flex; align-items:center; justify-content:center;
    font-family:'Plus Jakarta Sans',sans-serif; font-weight:800; font-size:17px; letter-spacing:.5px;
    color:var(--gold); background:rgba(255,255,255,.06);
    border:1px solid rgba(195,155,78,.55);
}
.brand-kicker{
    font-size:10.5px; font-weight:700; letter-spacing:.16em; text-transform:uppercase;
    color:var(--gold); margin-bottom:5px;
}
.brand-title{
    font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700;
    color:#fff; line-height:1.2; letter-spacing:-.02em;
}
.header-meta{ display:flex; align-items:center; gap:26px; z-index:1; }
.meta-item{ text-align:right; }
.meta-label{
    font-size:10px; font-weight:600; letter-spacing:.14em; text-transform:uppercase;
    color:rgba(255,255,255,.55); display:block; margin-bottom:3px;
}
.meta-value{ font-size:13.5px; font-weight:600; color:#fff; }
.meta-rule{ width:1px; height:34px; background:rgba(255,255,255,.16); }

/* ---------- ENCABEZADOS DE SECCIÓN ---------- */
.section{ margin:6px 0 14px 0; }
.section-eyebrow{
    font-size:10px; font-weight:700; letter-spacing:.16em; text-transform:uppercase;
    color:var(--gold); margin-bottom:4px;
}
.section-title{
    font-family:'Plus Jakarta Sans',sans-serif; font-size:17px; font-weight:700; color:var(--ink);
    letter-spacing:-.015em;
}
.section-sub{ font-size:12.5px; color:var(--muted); margin-top:3px; }

/* ---------- TARJETAS KPI ---------- */
.kpi{
    position:relative; background:#fff; border:1px solid var(--line); border-radius:var(--radius);
    padding:16px 18px 15px 20px; box-shadow:var(--shadow); height:100%;
    transition:transform .18s ease, box-shadow .18s ease;
}
.kpi:hover{ transform:translateY(-2px); box-shadow:0 10px 26px rgba(11,21,36,.10); }
.kpi::before{
    content:""; position:absolute; left:0; top:14px; bottom:14px; width:3px;
    border-radius:0 3px 3px 0; background:var(--navy);
}
.kpi-info::before{ background:var(--info); }
.kpi-ok::before{ background:var(--ok); }
.kpi-warn::before{ background:var(--warn); }
.kpi-danger::before{ background:var(--danger); }
.kpi-gold::before{ background:var(--gold); }

.kpi-label{
    font-size:10.5px; font-weight:700; letter-spacing:.13em; text-transform:uppercase;
    color:var(--muted); margin-bottom:8px;
}
.kpi-value{
    font-family:'Plus Jakarta Sans',sans-serif; font-size:32px; font-weight:800; line-height:1;
    color:var(--ink); font-variant-numeric:tabular-nums; letter-spacing:-.03em;
}
.kpi-sub{ font-size:11.5px; color:var(--muted); margin-top:8px; }

/* ---------- ETIQUETAS DE ESTADO ---------- */
.tag{
    display:inline-flex; align-items:center; gap:6px; padding:3px 10px; border-radius:999px;
    font-size:11px; font-weight:600; letter-spacing:.02em; border:1px solid transparent;
}
.tag::before{ content:""; width:6px; height:6px; border-radius:50%; background:currentColor; }
.tag-ok{ color:var(--ok); background:#ECFDF3; border-color:#C7EBD8; }
.tag-warn{ color:var(--warn); background:#FFF8EB; border-color:#F5DFB4; }
.tag-danger{ color:var(--danger); background:#FEF3F2; border-color:#F5CFCB; }
.tag-neutral{ color:var(--navy); background:#EEF3F9; border-color:#D8E3EF; }

/* ---------- DETALLE DENTRO DE CADA TRÁMITE ---------- */
.field-label{
    font-size:10px; font-weight:700; letter-spacing:.13em; text-transform:uppercase;
    color:var(--muted); margin-bottom:2px;
}
.field-value{ font-size:13.5px; color:var(--ink); font-weight:500; margin-bottom:14px; }

/* ---------- PESTAÑAS ---------- */
.stTabs [data-baseweb="tab-list"]{
    gap:4px; background:#fff; padding:6px; border-radius:var(--radius);
    border:1px solid var(--line); box-shadow:var(--shadow);
}
.stTabs [data-baseweb="tab"]{
    height:42px; border-radius:10px; padding:0 20px; background:transparent;
    font-family:'Plus Jakarta Sans',sans-serif; font-weight:600; font-size:13.5px; color:var(--muted);
    transition:all .18s ease;
}
.stTabs [data-baseweb="tab"]:hover{ background:var(--soft); color:var(--navy); }
.stTabs [aria-selected="true"]{ background:var(--navy) !important; color:#fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{ display:none; }
.stTabs [data-baseweb="tab-panel"]{ padding-top:22px; }

/* ---------- CONTROLES ---------- */
.stButton > button, [data-testid="stFormSubmitButton"] button{
    border-radius:10px; border:1px solid var(--line); background:#fff; color:var(--ink);
    font-family:'Plus Jakarta Sans',sans-serif; font-weight:600; font-size:13px;
    padding:.5rem 1rem; transition:all .18s ease; box-shadow:none;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover{
    border-color:var(--navy); color:var(--navy); background:var(--soft); transform:translateY(-1px);
}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"],
[data-testid="baseButton-primary"], [data-testid="baseButton-primaryFormSubmit"]{
    background:var(--navy) !important; color:#fff !important; border-color:var(--navy) !important;
}
.stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
[data-testid="baseButton-primary"]:hover, [data-testid="baseButton-primaryFormSubmit"]:hover{
    background:var(--navy-700) !important; box-shadow:0 8px 18px rgba(14,42,71,.22) !important;
}
.stButton > button:focus-visible, [data-testid="stFormSubmitButton"] button:focus-visible{
    outline:2px solid var(--gold); outline-offset:2px;
}

.stTextInput input, .stTextArea textarea, .stDateInput input{
    border-radius:10px !important; border:1px solid var(--line) !important;
    background:#fff !important; font-size:13.5px !important; color:var(--ink) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus{
    border-color:var(--navy) !important; box-shadow:0 0 0 3px rgba(14,42,71,.10) !important;
}
[data-baseweb="select"] > div{
    border-radius:10px !important; border-color:var(--line) !important; background:#fff !important;
    font-size:13.5px !important;
}
[data-baseweb="tag"]{ background:var(--navy) !important; border-radius:7px !important; }
.stMultiSelect [data-baseweb="select"] > div{ min-height:42px; }
label, .stRadio label, .stSelectbox label, .stMultiSelect label{
    font-size:12px !important; font-weight:600 !important; color:#334155 !important;
    letter-spacing:.01em;
}

/* ---------- FORMULARIO Y EXPANSORES COMO TARJETAS ---------- */
[data-testid="stForm"]{
    background:#fff; border:1px solid var(--line); border-radius:18px;
    padding:24px 26px; box-shadow:var(--shadow);
}
[data-testid="stExpander"]{
    background:#fff; border:1px solid var(--line) !important; border-radius:var(--radius) !important;
    box-shadow:0 1px 2px rgba(11,21,36,.04); margin-bottom:10px; overflow:hidden;
}
[data-testid="stExpander"] summary{
    padding:14px 18px !important; font-size:13.5px !important; font-weight:600 !important;
    color:var(--ink) !important;
}
[data-testid="stExpander"] summary:hover{ background:var(--soft); }
[data-testid="stExpander"] details > div{ border-top:1px solid var(--line); padding-top:14px; }

/* ---------- TABLAS Y AVISOS ---------- */
[data-testid="stDataFrame"]{
    border:1px solid var(--line); border-radius:var(--radius); overflow:hidden; background:#fff;
    box-shadow:var(--shadow);
}
[data-testid="stAlert"]{ border-radius:12px; border:1px solid var(--line); font-size:13.5px; }
[data-testid="stMetricValue"]{ font-family:'Plus Jakarta Sans',sans-serif; }

/* ---------- PANEL DE FILTROS ---------- */
.filter-shell{
    background:#fff; border:1px solid var(--line); border-radius:var(--radius);
    padding:6px 18px 2px 18px; box-shadow:var(--shadow); margin-bottom:6px;
}

/* ---------- PIE ---------- */
.app-footer{
    margin-top:34px; padding-top:16px; border-top:1px solid var(--line);
    display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px;
    font-size:11.5px; color:var(--muted);
}
.app-footer strong{ color:var(--navy); font-weight:600; }

/* ---------- RESPONSIVO ---------- */
@media (max-width:820px){
    .app-header{ padding:18px; }
    .brand-title{ font-size:18px; }
    .header-meta{ width:100%; justify-content:flex-start; }
    .meta-item{ text-align:left; }
    .kpi-value{ font-size:26px; }
}
@media (prefers-reduced-motion: reduce){
    *{ transition:none !important; animation:none !important; }
    .kpi:hover{ transform:none; }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# COMPONENTES REUTILIZABLES
# =========================================================
def kpi(label, value, sub="", tono="navy"):
    """Devuelve el HTML de una tarjeta KPI."""
    clases = {
        "navy": "", "info": "kpi-info", "ok": "kpi-ok",
        "warn": "kpi-warn", "danger": "kpi-danger", "gold": "kpi-gold"
    }
    return (
        f'<div class="kpi {clases.get(tono, "")}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>'
    )

def seccion(eyebrow, titulo, subtitulo=""):
    sub = f'<div class="section-sub">{subtitulo}</div>' if subtitulo else ""
    st.markdown(
        f'<div class="section"><div class="section-eyebrow">{eyebrow}</div>'
        f'<div class="section-title">{titulo}</div>{sub}</div>',
        unsafe_allow_html=True
    )

def campo(label, valor):
    return f'<div class="field-label">{label}</div><div class="field-value">{valor}</div>'

TAG_CLASE = {
    "EN PLAZO": "tag-ok",
    "SEGUIMIENTO": "tag-warn",
    "VENCIDO": "tag-danger",
    "FINIQUITADO": "tag-neutral"
}

def tag(estado):
    return f'<span class="tag {TAG_CLASE.get(estado, "tag-neutral")}">{estado}</span>'

PALETA = {
    "FINIQUITADO": "#0E2A47",
    "EN PLAZO": "#0F7B4F",
    "SEGUIMIENTO": "#C08228",
    "VENCIDO": "#B42318"
}

def estilo_grafico(fig, alto=330, leyenda=True):
    fig.update_layout(
        font=dict(family="Inter, sans-serif", size=12, color="#475569"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=14, b=10, l=10, r=10),
        height=alto,
        showlegend=leyenda,
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, x=0,
                    title_text="", font=dict(size=11)),
        hoverlabel=dict(bgcolor="#0E2A47", bordercolor="#0E2A47",
                        font=dict(color="#ffffff", family="Inter", size=12))
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EEF2F7", zeroline=False,
                     title_text="", linecolor="#E3E9F1")
    fig.update_yaxes(showgrid=False, zeroline=False, title_text="", linecolor="#E3E9F1")
    return fig

# =========================================================
# BASE DE DATOS
# =========================================================
DB_NAME = "gestion_correos.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS correos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mesa_entrada TEXT,
            remitente TEXT NOT NULL,
            asunto TEXT NOT NULL,
            tipo_documento TEXT DEFAULT 'Correo Electrónico',
            area_derivada TEXT NOT NULL,
            prioridad TEXT DEFAULT 'Normal',
            registrado_por TEXT,
            fecha_derivacion DATE NOT NULL,
            estado TEXT NOT NULL DEFAULT 'PENDIENTE',
            fecha_finiquito DATE,
            observaciones TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def cargar_datos():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM correos", conn)
    conn.close()
    return df

def ejecutar(sql, params=()):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(sql, params)
    conn.commit()
    conn.close()

def calcular_estado_automatico(fecha_derivacion_str, estado_actual):
    if estado_actual == "FINIQUITADO":
        return "FINIQUITADO", 0
    if isinstance(fecha_derivacion_str, str):
        fecha_deriv = datetime.strptime(fecha_derivacion_str, "%Y-%m-%d").date()
    else:
        fecha_deriv = fecha_derivacion_str
    dias_transcurridos = (date.today() - fecha_deriv).days
    if dias_transcurridos <= 3:
        return "EN PLAZO", dias_transcurridos
    elif 4 <= dias_transcurridos <= 8:
        return "SEGUIMIENTO", dias_transcurridos
    else:
        return "VENCIDO", dias_transcurridos

AREAS_LIST = ["DGFR", "DGI", "DGFI", "DINAEM", "DGCGAT", "Otra Área / Externa"]
TIPOS_DOC = ["Correo Electrónico", "Nota Oficial", "Nota Externa",
             "Informe Técnico", "Directiva / Resolución", "Otro"]
PRIORIDADES = ["Normal", "Alta", "Baja"]
RESPONSABLES = ["Gabinete / Jefatura", "Secretaría de Gabinete", "Asistente Técnico"]

MESES_ESP = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# =========================================================
# ENCABEZADO INSTITUCIONAL
# =========================================================
hoy = date.today()
fecha_larga = f"{hoy.day:02d} de {MESES_ESP[hoy.month]} de {hoy.year}"

df = cargar_datos()
total_registros = len(df)

st.markdown(f"""
<div class="app-header">
    <div class="brand">
        <div class="brand-mark">VM</div>
        <div>
            <div class="brand-kicker">Gabinete · Viceministerio de Mipymes</div>
            <div class="brand-title">Sistema de Control de Gestión y Derivaciones</div>
        </div>
    </div>
    <div class="header-meta">
        <div class="meta-item">
            <span class="meta-label">Fecha de sesión</span>
            <span class="meta-value">{fecha_larga}</span>
        </div>
        <div class="meta-rule"></div>
        <div class="meta-item">
            <span class="meta-label">Trámites en base</span>
            <span class="meta-value">{total_registros}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

tab1, tab2, tab3, tab4 = st.tabs([
    "Bandeja de derivaciones",
    "Registrar derivación",
    "Panel ejecutivo",
    "Base consolidada"
])

# =========================================================
# TAB 1: BANDEJA DE DERIVACIONES
# =========================================================
with tab1:
    seccion("Control de plazos", "Casos activos",
            "Los trámites se clasifican automáticamente: hasta 3 días en plazo, de 4 a 8 días en seguimiento, más de 8 días vencido.")

    if df.empty:
        st.info("Todavía no hay trámites cargados. Registrá el primero en la pestaña **Registrar derivación**.")
    else:
        df_pendientes = df[df["estado"] != "FINIQUITADO"].copy()

        if df_pendientes.empty:
            st.success("No quedan trámites pendientes. Toda la mesa está finiquitada.")
        else:
            estados_calculados, dias_list = [], []
            for _, row in df_pendientes.iterrows():
                st_calc, dias = calcular_estado_automatico(row["fecha_derivacion"], row["estado"])
                estados_calculados.append(st_calc)
                dias_list.append(dias)
            df_pendientes["Estado_Dinamico"] = estados_calculados
            df_pendientes["Dias_Transcurridos"] = dias_list

            # KPIs de la bandeja
            tot_pend = len(df_pendientes)
            tot_plazo = len(df_pendientes[df_pendientes["Estado_Dinamico"] == "EN PLAZO"])
            tot_seg = len(df_pendientes[df_pendientes["Estado_Dinamico"] == "SEGUIMIENTO"])
            tot_venc = len(df_pendientes[df_pendientes["Estado_Dinamico"] == "VENCIDO"])

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(kpi("Pendientes totales", tot_pend, "Trámites activos en gestión", "info"), unsafe_allow_html=True)
            with c2:
                st.markdown(kpi("En plazo", tot_plazo, "Hasta 3 días de derivados", "ok"), unsafe_allow_html=True)
            with c3:
                st.markdown(kpi("En seguimiento", tot_seg, "Entre 4 y 8 días", "warn"), unsafe_allow_html=True)
            with c4:
                st.markdown(kpi("Vencidos", tot_venc, "Más de 8 días sin respuesta", "danger"), unsafe_allow_html=True)

            st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

            # Filtros
            st.markdown('<div class="filter-shell">', unsafe_allow_html=True)
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                filtro_area = st.multiselect("Dirección o área", options=sorted(df_pendientes["area_derivada"].unique()))
            with col_f2:
                filtro_estado = st.multiselect("Estado del plazo", options=["EN PLAZO", "SEGUIMIENTO", "VENCIDO"])
            with col_f3:
                filtro_prio = st.multiselect("Prioridad", options=PRIORIDADES)
            st.markdown('</div>', unsafe_allow_html=True)

            df_filtrado = df_pendientes.copy()
            if filtro_area:
                df_filtrado = df_filtrado[df_filtrado["area_derivada"].isin(filtro_area)]
            if filtro_estado:
                df_filtrado = df_filtrado[df_filtrado["Estado_Dinamico"].isin(filtro_estado)]
            if filtro_prio:
                df_filtrado = df_filtrado[df_filtrado["prioridad"].isin(filtro_prio)]

            df_filtrado = df_filtrado.sort_values("Dias_Transcurridos", ascending=False)

            # Panel de edición
            if st.session_state.edit_id is not None:
                registro_editar = df[df["id"] == st.session_state.edit_id]
                if not registro_editar.empty:
                    row_e = registro_editar.iloc[0]
                    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                    seccion("Edición", f"Trámite N° {row_e['id']}", row_e['asunto'])

                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        edit_remitente = st.text_input("Remitente", value=str(row_e['remitente']), key="e_rem")
                        edit_asunto = st.text_input("Asunto", value=str(row_e['asunto']), key="e_asu")
                        idx_tipo = TIPOS_DOC.index(row_e['tipo_documento']) if row_e.get('tipo_documento') in TIPOS_DOC else 0
                        edit_tipo = st.selectbox("Tipo de documento", TIPOS_DOC, index=idx_tipo, key="e_tip")
                        edit_mesa = st.text_input("N° de mesa de entrada o referencia", value=str(row_e.get('mesa_entrada') or ''), key="e_mes")
                    with col_e2:
                        idx_area = AREAS_LIST.index(row_e['area_derivada']) if row_e['area_derivada'] in AREAS_LIST else 0
                        edit_area = st.selectbox("Dirección o área derivada", AREAS_LIST, index=idx_area, key="e_are")
                        idx_prio = PRIORIDADES.index(row_e.get('prioridad', 'Normal')) if row_e.get('prioridad') in PRIORIDADES else 0
                        edit_prioridad = st.radio("Prioridad", PRIORIDADES, index=idx_prio, horizontal=True, key="e_pri")
                        f_date = datetime.strptime(str(row_e['fecha_derivacion']), "%Y-%m-%d").date() if isinstance(row_e['fecha_derivacion'], str) else row_e['fecha_derivacion']
                        edit_fecha = st.date_input("Fecha de derivación", value=f_date, key="e_fec")
                        idx_resp = RESPONSABLES.index(row_e.get('registrado_por')) if row_e.get('registrado_por') in RESPONSABLES else 0
                        edit_registrado = st.selectbox("Registrado por", RESPONSABLES, index=idx_resp, key="e_res")

                    edit_obs = st.text_area("Observaciones", value=str(row_e['observaciones'] or ''), key="e_obs")

                    btn_c1, btn_c2, _ = st.columns([1, 1, 3])
                    with btn_c1:
                        if st.button("Guardar cambios", type="primary", use_container_width=True):
                            ejecutar("""
                                UPDATE correos SET remitente = ?, asunto = ?, tipo_documento = ?, mesa_entrada = ?,
                                area_derivada = ?, prioridad = ?, fecha_derivacion = ?, registrado_por = ?, observaciones = ?
                                WHERE id = ?
                            """, (edit_remitente, edit_asunto, edit_tipo, edit_mesa, edit_area, edit_prioridad,
                                  edit_fecha.strftime("%Y-%m-%d"), edit_registrado, edit_obs, int(row_e['id'])))
                            st.session_state.edit_id = None
                            st.rerun()
                    with btn_c2:
                        if st.button("Cancelar", use_container_width=True):
                            st.session_state.edit_id = None
                            st.rerun()
                    st.markdown("---")

            # Listado de trámites
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            marcador = {"EN PLAZO": "🟢", "SEGUIMIENTO": "🟡", "VENCIDO": "🔴"}

            if df_filtrado.empty:
                st.warning("Ningún trámite coincide con los filtros aplicados.")
            else:
                for _, row in df_filtrado.iterrows():
                    mesa_val = row.get('mesa_entrada', '')
                    ref_doc = f"Ref. {mesa_val}  ·  " if mesa_val else ""
                    titulo = (
                        f"{marcador.get(row['Estado_Dinamico'], '')}  {row['asunto']}"
                        f"     ·     {ref_doc}{row['area_derivada']}"
                        f"  ·  {row['Estado_Dinamico']} · {row['Dias_Transcurridos']} día(s)"
                    )
                    with st.expander(titulo):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.markdown(
                                campo("Remitente", row['remitente']) +
                                campo("Tipo de documento", row.get('tipo_documento', 'Correo Electrónico')) +
                                campo("Observaciones", row['observaciones'] or "Sin observaciones registradas."),
                                unsafe_allow_html=True
                            )
                        with col2:
                            st.markdown(
                                campo("Dirección o área", row['area_derivada']) +
                                campo("Fecha de derivación", row['fecha_derivacion']) +
                                campo("Registrado por", row.get('registrado_por', 'Gabinete')) +
                                f'<div class="field-label">Situación</div><div class="field-value">'
                                f'{tag(row["Estado_Dinamico"])} &nbsp; <span style="color:#64748B">'
                                f'{row["Dias_Transcurridos"]} día(s) · prioridad {row.get("prioridad", "Normal")}</span></div>',
                                unsafe_allow_html=True
                            )
                        with col3:
                            if st.button("Finiquitar", key=f"fin_{row['id']}", type="primary", use_container_width=True):
                                ejecutar("UPDATE correos SET estado = 'FINIQUITADO', fecha_finiquito = ? WHERE id = ?",
                                         (date.today().strftime("%Y-%m-%d"), int(row['id'])))
                                st.rerun()
                            if st.button("Editar", key=f"btn_edit_{row['id']}", use_container_width=True):
                                st.session_state.edit_id = row['id']
                                st.rerun()
                            if st.button("Eliminar", key=f"del_{row['id']}", use_container_width=True):
                                ejecutar("DELETE FROM correos WHERE id = ?", (int(row['id']),))
                                st.rerun()

# =========================================================
# TAB 2: REGISTRO DE DERIVACIONES
# =========================================================
with tab2:
    seccion("Mesa de entrada", "Registrar una nueva derivación",
            "Los campos Remitente y Asunto son obligatorios. El plazo empieza a correr desde la fecha de derivación.")

    with st.form("form_gabinete", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            remitente = st.text_input("Remitente", placeholder="Institución o persona que remite")
            asunto = st.text_input("Asunto o resumen", placeholder="Detalle breve del trámite")
            tipo_documento = st.selectbox("Tipo de documento", TIPOS_DOC)
            mesa_entrada = st.text_input("N° de mesa de entrada o referencia", placeholder="Opcional")
        with col_b:
            area_derivada = st.selectbox("Dirección o área a la que se deriva", AREAS_LIST)
            prioridad = st.radio("Prioridad del trámite", PRIORIDADES, horizontal=True)
            fecha_derivacion = st.date_input("Fecha de derivación", value=date.today())
            registrado_por = st.selectbox("Registrado por", RESPONSABLES)

        observaciones = st.text_area("Observaciones o instrucciones", placeholder="Indicaciones para el área receptora")
        submitted = st.form_submit_button("Registrar y derivar trámite", type="primary", use_container_width=True)

        if submitted:
            if remitente.strip() and asunto.strip():
                ejecutar("""
                    INSERT INTO correos (mesa_entrada, remitente, asunto, tipo_documento, area_derivada,
                    prioridad, registrado_por, fecha_derivacion, estado, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDIENTE', ?)
                """, (mesa_entrada, remitente, asunto, tipo_documento, area_derivada, prioridad,
                      registrado_por, fecha_derivacion.strftime("%Y-%m-%d"), observaciones))
                st.success("Trámite registrado y derivado. Ya figura en la bandeja de derivaciones.")
                st.rerun()
            else:
                st.error("Faltan datos obligatorios: completá Remitente y Asunto.")

# =========================================================
# TAB 3: PANEL EJECUTIVO
# =========================================================
with tab3:
    seccion("Analítica de gestión", "Panel ejecutivo",
            "Indicadores de cumplimiento, carga por dirección y evolución de las derivaciones.")

    if df.empty:
        st.info("El panel se activa en cuanto existan trámites registrados.")
    else:
        df_pb = df.copy()
        df_pb["dt_fecha"] = pd.to_datetime(df_pb["fecha_derivacion"])
        df_pb["Año"] = df_pb["dt_fecha"].dt.year
        df_pb["Num_Mes"] = df_pb["dt_fecha"].dt.month
        df_pb["Nombre_Mes"] = df_pb["Num_Mes"].map(MESES_ESP)

        estados_powerbi, dias_powerbi = [], []
        for _, r in df_pb.iterrows():
            st_calc, dias = calcular_estado_automatico(r["fecha_derivacion"], r["estado"])
            estados_powerbi.append(st_calc)
            dias_powerbi.append(dias)
        df_pb["Estado_Plazo"] = estados_powerbi
        df_pb["Dias_Transcurridos"] = dias_powerbi

        st.markdown('<div class="filter-shell">', unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            anos_disponibles = sorted(df_pb["Año"].unique().tolist(), reverse=True)
            f_ano = st.multiselect("Año", options=anos_disponibles, default=anos_disponibles)
        with col_f2:
            df_m = df_pb[df_pb["Año"].isin(f_ano)] if f_ano else df_pb
            meses_ord = df_m.sort_values("Num_Mes")["Nombre_Mes"].unique().tolist()
            f_mes = st.multiselect("Mes", options=meses_ord, default=meses_ord)
        with col_f3:
            areas_disp = sorted(df_pb["area_derivada"].unique().tolist())
            f_direccion = st.multiselect("Dirección", options=areas_disp, default=areas_disp)
        st.markdown('</div>', unsafe_allow_html=True)

        df_dash = df_pb.copy()
        if f_ano:
            df_dash = df_dash[df_dash["Año"].isin(f_ano)]
        if f_mes:
            df_dash = df_dash[df_dash["Nombre_Mes"].isin(f_mes)]
        if f_direccion:
            df_dash = df_dash[df_dash["area_derivada"].isin(f_direccion)]

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        if df_dash.empty:
            st.warning("No hay registros para los filtros seleccionados. Ampliá el rango o quitá algún filtro.")
        else:
            total_casos = len(df_dash)
            tot_finiquitados = len(df_dash[df_dash["Estado_Plazo"] == "FINIQUITADO"])
            tot_pendientes = total_casos - tot_finiquitados
            tot_vencidos = len(df_dash[df_dash["Estado_Plazo"] == "VENCIDO"])
            pct_eficiencia = round((tot_finiquitados / total_casos) * 100, 1) if total_casos > 0 else 0
            promedio_dias = round(df_dash[df_dash["estado"] != "FINIQUITADO"]["Dias_Transcurridos"].mean(), 1) if tot_pendientes > 0 else 0

            k1, k2, k3, k4, k5 = st.columns(5)
            with k1:
                st.markdown(kpi("Total de trámites", total_casos, "Casos en el período filtrado", "info"), unsafe_allow_html=True)
            with k2:
                st.markdown(kpi("Finiquitados", tot_finiquitados, f"{pct_eficiencia}% de cumplimiento", "ok"), unsafe_allow_html=True)
            with k3:
                st.markdown(kpi("Pendientes", tot_pendientes, "En gestión de las direcciones", "warn"), unsafe_allow_html=True)
            with k4:
                st.markdown(kpi("Vencidos", tot_vencidos, "Más de 8 días sin respuesta", "danger"), unsafe_allow_html=True)
            with k5:
                st.markdown(kpi("Espera promedio", promedio_dias, "Días acumulados por trámite", "gold"), unsafe_allow_html=True)

            st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)

            col_ch1, col_ch2 = st.columns([1, 1.25])
            with col_ch1:
                seccion("Composición", "Distribución por estado")
                conteo_estados = df_dash["Estado_Plazo"].value_counts().reset_index()
                conteo_estados.columns = ["Estado", "Cantidad"]
                fig_donut = px.pie(conteo_estados, names="Estado", values="Cantidad", hole=0.62,
                                   color="Estado", color_discrete_map=PALETA)
                fig_donut.update_traces(
                    textposition="outside", textinfo="percent",
                    marker=dict(line=dict(color="#ffffff", width=3)),
                    hovertemplate="%{label}: %{value} trámites<extra></extra>"
                )
                estilo_grafico(fig_donut, 340)
                fig_donut.add_annotation(
                    text=f"<b>{total_casos}</b><br><span style='font-size:11px;color:#64748B'>trámites</span>",
                    showarrow=False, font=dict(family="Plus Jakarta Sans", size=26, color="#0B1524")
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            with col_ch2:
                seccion("Carga operativa", "Trámites por dirección")
                df_area = df_dash.groupby(["area_derivada", "Estado_Plazo"]).size().reset_index(name="Cantidad")
                fig_bar = px.bar(df_area, y="area_derivada", x="Cantidad", color="Estado_Plazo",
                                 orientation="h", color_discrete_map=PALETA, barmode="stack")
                fig_bar.update_traces(marker_line_width=0, hovertemplate="%{y} · %{x} trámites<extra></extra>")
                estilo_grafico(fig_bar, 340)
                fig_bar.update_layout(bargap=0.35)
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            seccion("Evolución", "Derivaciones por mes",
                    "Volumen mensual de trámites ingresados según el estado actual de su plazo.")
            df_evo = (df_dash.groupby(["Año", "Num_Mes", "Nombre_Mes", "Estado_Plazo"])
                      .size().reset_index(name="Cantidad")
                      .sort_values(["Año", "Num_Mes"]))
            df_evo["Periodo"] = df_evo["Nombre_Mes"].str[:3] + " " + df_evo["Año"].astype(str)
            fig_evo = px.bar(df_evo, x="Periodo", y="Cantidad", color="Estado_Plazo",
                             color_discrete_map=PALETA, barmode="stack")
            fig_evo.update_traces(marker_line_width=0, hovertemplate="%{x} · %{y} trámites<extra></extra>")
            estilo_grafico(fig_evo, 300)
            fig_evo.update_layout(bargap=0.5)
            st.plotly_chart(fig_evo, use_container_width=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            seccion("Alerta de gestión", "Veinte trámites con mayor tiempo en espera",
                    "Ordenados de mayor a menor antigüedad, excluye los ya finiquitados.")

            df_sin_finiquitar = df_dash[df_dash["estado"] != "FINIQUITADO"].copy()
            if df_sin_finiquitar.empty:
                st.success("No hay trámites pendientes en el período filtrado.")
            else:
                top_20 = df_sin_finiquitar.sort_values(by="Dias_Transcurridos", ascending=False).head(20)
                top_20_display = top_20[["id", "mesa_entrada", "asunto", "remitente", "area_derivada",
                                         "prioridad", "fecha_derivacion", "Dias_Transcurridos", "Estado_Plazo"]].copy()
                top_20_display.rename(columns={
                    "id": "N°", "mesa_entrada": "Mesa de entrada", "asunto": "Asunto",
                    "remitente": "Remitente", "area_derivada": "Dirección responsable",
                    "prioridad": "Prioridad", "fecha_derivacion": "Fecha de derivación",
                    "Dias_Transcurridos": "Días acumulados", "Estado_Plazo": "Estado del plazo"
                }, inplace=True)

                st.dataframe(
                    top_20_display, use_container_width=True, hide_index=True,
                    column_config={
                        "N°": st.column_config.NumberColumn("N°", format="%d", width="small"),
                        "Asunto": st.column_config.TextColumn("Asunto", width="large"),
                        "Días acumulados": st.column_config.ProgressColumn(
                            "Días acumulados", format="%d días", min_value=0,
                            max_value=max(int(top_20_display["Días acumulados"].max()), 10)
                        )
                    }
                )

# =========================================================
# TAB 4: BASE CONSOLIDADA
# =========================================================
with tab4:
    seccion("Datos", "Base consolidada de gestión",
            "Descargá la base completa para trabajarla en Power BI o en Excel.")

    if df.empty:
        st.info("No hay registros para exportar todavía.")
    else:
        df_export = df.copy()
        estados_powerbi, dias_powerbi = [], []
        for _, row in df_export.iterrows():
            st_calc, dias = calcular_estado_automatico(row["fecha_derivacion"], row["estado"])
            estados_powerbi.append(st_calc)
            dias_powerbi.append(dias if row["estado"] != "FINIQUITADO" else 0)
        df_export["Estado_Plazo"] = estados_powerbi
        df_export["Dias_Transcurridos"] = dias_powerbi

        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(kpi("Registros", len(df_export), "Filas disponibles para exportar", "info"), unsafe_allow_html=True)
        with r2:
            st.markdown(kpi("Direcciones", df_export["area_derivada"].nunique(), "Áreas con trámites derivados", "gold"), unsafe_allow_html=True)
        with r3:
            st.markdown(kpi("Última carga", str(df_export["fecha_derivacion"].max()), "Fecha de derivación más reciente"), unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.dataframe(df_export, use_container_width=True, hide_index=True, height=420)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        c_down1, c_down2, _ = st.columns([1, 1, 2])
        with c_down1:
            csv_data = df_export.to_csv(index=False).encode("utf-8-sig")
            st.download_button("Descargar CSV", data=csv_data, file_name="gestion_gabinete.csv",
                               mime="text/csv", type="primary", use_container_width=True)
        with c_down2:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_export.to_excel(writer, index=False, sheet_name="Gestion_Gabinete")
            st.download_button(
                "Descargar Excel", data=buffer.getvalue(), file_name="reporte_gabinete.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# =========================================================
# PIE DE PÁGINA
# =========================================================
st.markdown(f"""
<div class="app-footer">
    <div><strong>Gabinete del Viceministerio de Mipymes</strong> · Sistema de Control de Gestión y Derivaciones</div>
    <div>Actualizado al {fecha_larga}</div>
</div>
""", unsafe_allow_html=True)
