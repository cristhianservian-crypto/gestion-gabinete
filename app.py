import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl

# =========================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS PRO
# =========================================================
st.set_page_config(
    page_title="Sistema de Gestión - Gabinete MIC",
    page_icon="💼",
    layout="wide"
)

# Estilos CSS Personalizados estilo Empresa Pro / SaaS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Fondo general */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }

    /* Sidebar elegante */
    section[data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Título principal con degradado estilo Netflix/Stripe */
    .main-title {
        font-size: 2.5rem !important;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .sub-title {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }

    /* Tarjetas contenedoras de información */
    .pro-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
    }

    /* Botones modernos con efecto Hover */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(79, 70, 229, 0.5);
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
    }

    /* Modificar campos de texto (Inputs) */
    div[data-baseweb="input"] {
        background-color: #1e293b !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
        color: white !important;
    }

    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. FUNCIONES DE BASE DE DATOS Y AUTENTICACIÓN
# =========================================================
FILE_DB = "gestion_gabinete.xlsx"

def cargar_datos():
    try:
        return pd.read_excel(FILE_DB, sheet_name="Documentos")
    except Exception:
        return pd.DataFrame(columns=[
            "ID", "Nro_Mesa_Entrada", "Fecha_Ingreso", "Remitente_Institucion",
            "Objeto_Resumen", "Asignado_A", "Plazo_Respuesta", "Estado",
            "Nro_Nota_Respuesta", "Observaciones"
        ])

def guardar_datos(df):
    with pd.ExcelWriter(FILE_DB, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Documentos", index=False)

def inicializar_sesion():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "role" not in st.session_state:
        st.session_state.role = None

USUARIOS = {
    "admin": {"pass": "admin123", "role": "Administrador"},
    "usuario1": {"pass": "user123", "role": "Operador"},
    "viceministro": {"pass": "vice2026", "role": "Lector"}
}

inicializar_sesion()

# =========================================================
# 3. PANTALLA DE LOGIN
# =========================================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="pro-card" style="text-align: center;">
            <h1 class="main-title">Gabinete MIC</h1>
            <p class="sub-title">Plataforma de Gestión de Documentos</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("Usuario")
            pass_input = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit:
                if user_input in USUARIOS and USUARIOS[user_input]["pass"] == pass_input:
                    st.session_state.logged_in = True
                    st.session_state.user = user_input
                    st.session_state.role = USUARIOS[user_input]["role"]
                    st.success("¡Bienvenido!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

# =========================================================
# 4. SISTEMA PRINCIPAL (PANEL DE CONTROL)
# =========================================================
else:
    # Sidebar
    st.sidebar.markdown(f"### 👤 **{st.session_state.user.upper()}**")
    st.sidebar.caption(f"Rol: {st.session_state.role}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Navegación", ["Dashboard / Resumen", "Registro de Documentos", "Consulta y Filtros"])

    df_docs = cargar_datos()

    # ENCABEZADO PRINCIPAL
    st.markdown('<h1 class="main-title">Sistema de Gestión de Gabinete</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Viceministerio de Mypimes - Control y Seguimiento Documental</p>', unsafe_allow_html=True)

    # --- OPCIÓN 1: DASHBOARD ---
    if menu == "Dashboard / Resumen":
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        total_docs = len(df_docs)
        pendientes = len(df_docs[df_docs["Estado"] == "Pendiente"]) if not df_docs.empty else 0
        en_proceso = len(df_docs[df_docs["Estado"] == "En Proceso"]) if not df_docs.empty else 0
        finalizados = len(df_docs[df_docs["Estado"] == "Finalizado"]) if not df_docs.empty else 0

        col_m1.metric("Total Documentos", total_docs)
        col_m2.metric("Pendientes", pendientes)
        col_m3.metric("En Proceso", en_proceso)
        col_m4.metric("Finalizados", finalizados)

        st.markdown("---")

        if not df_docs.empty:
            c1, c2 = st.columns(2)
            with c1:
                fig_estado = px.pie(df_docs, names="Estado", title="Distribución por Estado", hole=0.4,
                                    color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_estado.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig_estado, use_container_width=True)

            with c2:
                fig_asig = px.bar(df_docs, x="Asignado_A", title="Documentos por Encargado",
                                  color_discrete_sequence=['#38bdf8'])
                fig_asig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig_asig, use_container_width=True)
        else:
            st.info("Aún no hay documentos registrados para mostrar gráficos.")

    # --- OPCIÓN 2: REGISTRO ---
    elif menu == "Registro de Documentos":
        st.markdown('<div class="pro-card"><h3>📋 Registrar Nuevo Documento</h3></div>', unsafe_allow_html=True)
        
        with st.form("form_registro"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                nro_mesa = st.text_input("Nro. Mesa de Entrada *")
                fecha_ingreso = st.date_input("Fecha de Ingreso")
                remitente = st.text_input("Remitente / Institución *")
                objeto = st.text_area("Objeto / Resumen *")

            with col_b:
                asignado = st.selectbox("Asignado A", ["Director 1", "Asesor Legal", "Técnico A", "Secretaría Viceministerio"])
                plazo = st.date_input("Plazo de Respuesta")
                estado = st.selectbox("Estado Inicial", ["Pendiente", "En Proceso", "Finalizado"])
                nro_nota = st.text_input("Nro. Nota Respuesta (Opcional)")
                obs = st.text_input("Observaciones")

            guardar = st.form_submit_button("Guardar Documento")

            if guardar:
                if not nro_mesa or not remitente or not objeto:
                    st.warning("Por favor completa los campos obligatorios (*)")
                else:
                    nuevo_id = 1 if df_docs.empty else int(df_docs["ID"].max()) + 1
                    nuevo_doc = {
                        "ID": nuevo_id,
                        "Nro_Mesa_Entrada": nro_mesa,
                        "Fecha_Ingreso": str(fecha_ingreso),
                        "Remitente_Institucion": remitente,
                        "Objeto_Resumen": objeto,
                        "Asignado_A": asignado,
                        "Plazo_Respuesta": str(plazo),
                        "Estado": estado,
                        "Nro_Nota_Respuesta": nro_nota,
                        "Observaciones": obs
                    }
                    df_docs = pd.concat([df_docs, pd.DataFrame([nuevo_doc])], ignore_index=True)
                    guardar_datos(df_docs)
                    st.success(f"¡Documento Nro. {nro_mesa} guardado exitosamente!")

    # --- OPCIÓN 3: CONSULTA ---
    elif menu == "Consulta y Filtros":
        st.markdown('<div class="pro-card"><h3>🔍 Listado e Historial de Documentos</h3></div>', unsafe_allow_html=True)
        
        if not df_docs.empty:
            # Buscador
            busqueda = st.text_input("🔎 Buscar por Nro. Mesa de Entrada, Remitente u Objeto:")
            
            df_mostrar = df_docs.copy()
            if busqueda:
                mask = df_mostrar.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
                df_mostrar = df_mostrar[mask]

            st.dataframe(df_mostrar, use_container_width=True)
        else:
            st.info("La base de datos está vacía por el momento.")
