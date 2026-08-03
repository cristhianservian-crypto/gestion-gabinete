import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, date

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Gabinete Viceministerio de Mipymes - Control de Gestión",
    page_icon="🏛️",
    layout="wide"
)

# ---------------------------------------------------------
# DICCIONARIO DE USUARIOS AUTORIZADOS (GESTIÓN DE ACCESOS)
# Aquí configuras los usuarios y contraseñas autorizados.
# Puedes agregar a tu jefe, compañera o nuevos miembros.
# ---------------------------------------------------------
USERS_DB = {
    "gabinete": {
        "password": "mic2026", 
        "nombre": "Equipo de Gabinete", 
        "rol": "Gabinete"
    }
}

# ---------------------------------------------------------
# CONTROL DE SESIÓN (LOGIN)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_fullname" not in st.session_state:
    st.session_state.user_fullname = ""

def login_form():
    st.markdown("""
    <style>
        .login-box {
            max-width: 420px;
            margin: 50px auto;
            padding: 30px;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border-top: 5px solid #002855;
            text-align: center;
        }
        .login-title {
            font-size: 22px;
            font-weight: 700;
            color: #002855;
            margin-bottom: 5px;
        }
        .login-sub {
            font-size: 13px;
            color: #6c757d;
            margin-bottom: 25px;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-box">
            <p class="login-title">🏛️ Control de Gestión</p>
            <p class="login-sub">Gabinete del Viceministerio de Mipymes</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_login"):
            st.subheader("🔑 Acceso Restringido")
            usuario_input = st.text_input("Usuario:", placeholder="Ingresa tu usuario").strip().lower()
            password_input = st.text_input("Contraseña:", type="password", placeholder="Ingresa tu contraseña")
            btn_login = st.form_submit_button("Ingresar al Sistema", type="primary", use_container_width=True)
            
            if btn_login:
                if usuario_input in USERS_DB and USERS_DB[usuario_input]["password"] == password_input:
                    st.session_state.authenticated = True
                    st.session_state.user_fullname = USERS_DB[usuario_input]["nombre"]
                    st.success("✅ Acceso concedido.")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos. Solicita acceso al Administrador de Gabinete.")

# Si no está autenticado, mostrar formulario de login y detener ejecución
if not st.session_state.authenticated:
    login_form()
    st.stop()

# ---------------------------------------------------------
# SI ESTÁ AUTENTICADO: CARGAR PÁGINA PRINCIPAL
# ---------------------------------------------------------

# ESTILOS CSS INSTITUCIONALES TIPO POWER BI
st.markdown("""
<style>
    .stApp { background-color: #f4f6f9; }
    .header-box {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white; padding: 22px 28px; border-radius: 12px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.12); border-left: 6px solid #d4af37;
    }
    .header-title { font-size: 25px; font-weight: 700; margin: 0; }
    .header-subtitle { font-size: 14px; color: #e0e0e0; margin-top: 4px; }
    .kpi-card {
        background-color: #ffffff; border-radius: 10px; padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); border: 1px solid #e1e8ed;
        border-top: 4px solid #002855; text-align: center;
    }
    .kpi-card-danger { border-top: 4px solid #d9534f !important; }
    .kpi-card-warning { border-top: 4px solid #f0ad4e !important; }
    .kpi-card-success { border-top: 4px solid #5cb85c !important; }
    .kpi-title { font-size: 13px; font-weight: 600; color: #6c757d; text-transform: uppercase; margin-bottom: 6px; }
    .kpi-value { font-size: 28px; font-weight: 800; color: #1a252f; margin: 0; }
    .kpi-subtext { font-size: 11px; color: #8c9ba5; margin-top: 4px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0px 0px; padding: 10px 20px; background-color: #e2e8f0; font-weight: 600; color: #334155; }
    .stTabs [aria-selected="true"] { background-color: #0f172a !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# BASE DE DATOS
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

AREAS_LIST = [
    "Dirección General de Mipymes",
    "Dirección de Capacitación y Competitividad",
    "Dirección de Financiamiento",
    "Dirección de Formalización y Registro",
    "Asesoría Jurídica del Viceministerio",
    "Coordinación Administrativa",
    "Otra Área / Externa"
]

MESES_ESP = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# ENCABEZADO INSTITUCIONAL CON BOTÓN DE CERRAR SESIÓN
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.markdown(f"""
    <div class="header-box">
        <p class="header-title">🏛️ Sistema de Control de Gestión y Derivaciones</p>
        <p class="header-subtitle">Gabinete del Viceministerio de Mipymes | Usuario activo: <b>{st.session_state.user_fullname}</b></p>
    </div>
    """, unsafe_allow_html=True)
with col_head2:
    st.write("")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_fullname = ""
        st.rerun()

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

df = cargar_datos()

tab1, tab2, tab3, tab4 = st.tabs([
    "📥 Bandeja de Derivaciones", 
    "➕ Registrar Nueva Derivación", 
    "📊 Power BI Dashboard Executive",
    "📋 Base Consolidada (Exportar a Power BI)"
])

# TAB 1: BANDEJA DE DERIVACIONES
with tab1:
    st.markdown("##### 📌 Casos Activos y Control de Plazos Administrativos")
    if not df.empty:
        df_pendientes = df[df["estado"] != "FINIQUITADO"].copy()
        if not df_pendientes.empty:
            estados_calculados, dias_list = [], []
            for index, row in df_pendientes.iterrows():
                st_calc, dias = calcular_estado_automatico(row["fecha_derivacion"], row["estado"])
                estados_calculados.append(st_calc)
                dias_list.append(dias)
            df_pendientes["Estado_Dinamico"] = estados_calculados
            df_pendientes["Dias_Transcurridos"] = dias_list
            
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                filtro_area = st.multiselect("Filtrar por Área:", options=df_pendientes["area_derivada"].unique())
            with col_f2:
                filtro_estado = st.multiselect("Filtrar por Estado:", options=["EN PLAZO", "SEGUIMIENTO", "VENCIDO"])
            with col_f3:
                filtro_prio = st.multiselect("Filtrar por Prioridad:", options=["Alta", "Normal", "Baja"])
                
            df_filtrado = df_pendientes.copy()
            if filtro_area: df_filtrado = df_filtrado[df_filtrado["area_derivada"].isin(filtro_area)]
            if filtro_estado: df_filtrado = df_filtrado[df_filtrado["Estado_Dinamico"].isin(filtro_estado)]
            if filtro_prio: df_filtrado = df_filtrado[df_filtrado["prioridad"].isin(filtro_prio)]
                
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Pendientes Totales", len(df_pendientes))
            c2.metric("🟢 En Plazo", len(df_pendientes[df_pendientes["Estado_Dinamico"] == "EN PLAZO"]))
            c3.metric("🟡 En Seguimiento", len(df_pendientes[df_pendientes["Estado_Dinamico"] == "SEGUIMIENTO"]))
            c4.metric("🔴 Vencidos", len(df_pendientes[df_pendientes["Estado_Dinamico"] == "VENCIDO"]))
            st.markdown("---")
            
            if st.session_state.edit_id is not None:
                registro_editar = df[df["id"] == st.session_state.edit_id]
                if not registro_editar.empty:
                    row_e = registro_editar.iloc[0]
                    st.info(f"✏️ **Editando trámite ID #{row_e['id']}:** {row_e['asunto']}")
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        edit_remitente = st.text_input("Remitente:", value=str(row_e['remitente']), key="e_rem")
                        edit_asunto = st.text_input("Asunto:", value=str(row_e['asunto']), key="e_asu")
                        tipos = ["Correo Electrónico", "Nota Oficial", "Nota Externa", "Informe Técnico", "Directiva / Resolución", "Otro"]
                        idx_tipo = tipos.index(row_e['tipo_documento']) if row_e.get('tipo_documento') in tipos else 0
                        edit_tipo = st.selectbox("Tipo de Documento:", tipos, index=idx_tipo, key="e_tip")
                        edit_mesa = st.text_input("Nº Mesa de Entrada / Ref.:", value=str(row_e.get('mesa_entrada') or ''), key="e_mes")

                    with col_e2:
                        idx_area = AREAS_LIST.index(row_e['area_derivada']) if row_e['area_derivada'] in AREAS_LIST else 0
                        edit_area = st.selectbox("Área Derivada:", AREAS_LIST, index=idx_area, key="e_are")
                        prios = ["Normal", "Alta", "Baja"]
                        idx_prio = prios.index(row_e.get('prioridad', 'Normal')) if row_e.get('prioridad') in prios else 0
                        edit_prioridad = st.radio("Prioridad:", prios, index=idx_prio, horizontal=True, key="e_pri")
                        f_date = datetime.strptime(str(row_e['fecha_derivacion']), "%Y-%m-%d").date() if isinstance(row_e['fecha_derivacion'], str) else row_e['fecha_derivacion']
                        edit_fecha = st.date_input("Fecha Derivación:", value=f_date, key="e_fec")
                        resp_list = ["Gabinete / Jefatura", "Secretaría de Gabinete", "Asistente Técnico"]
                        idx_resp = resp_list.index(row_e.get('registrado_por')) if row_e.get('registrado_por') in resp_list else 0
                        edit_registrado = st.selectbox("Registrado por:", resp_list, index=idx_resp, key="e_res")

                    edit_obs = st.text_area("Observaciones:", value=str(row_e['observaciones'] or ''), key="e_obs")
                    btn_c1, btn_c2 = st.columns([1, 4])
                    with btn_c1:
                        if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                            conn = sqlite3.connect(DB_NAME)
                            c = conn.cursor()
                            c.execute("""
                                UPDATE correos SET remitente = ?, asunto = ?, tipo_documento = ?, mesa_entrada = ?, 
                                area_derivada = ?, prioridad = ?, fecha_derivacion = ?, registrado_por = ?, observaciones = ? WHERE id = ?
                            """, (edit_remitente, edit_asunto, edit_tipo, edit_mesa, edit_area, edit_prioridad, edit_fecha.strftime("%Y-%m-%d"), edit_registrado, edit_obs, int(row_e['id'])))
                            conn.commit()
                            conn.close()
                            st.session_state.edit_id = None
                            df = cargar_datos()
                            st.rerun()
                    with btn_c2:
                        if st.button("❌ Cancelar Edición"):
                            st.session_state.edit_id = None
                            st.rerun()
                    st.markdown("---")

            for _, row in df_filtrado.iterrows():
                color_map = {"EN PLAZO": "🟢 EN PLAZO", "SEGUIMIENTO": "🟡 SEGUIMIENTO", "VENCIDO": "🔴 VENCIDO"}
                mesa_val = row.get('mesa_entrada', '')
                ref_doc = f" [Mesa/Ref: {mesa_val}]" if mesa_val else ""
                with st.expander(f"📄 {row['asunto']}{ref_doc} | {row['area_derivada']} | {color_map.get(row['Estado_Dinamico'])} ({row['Dias_Transcurridos']} días)"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"**Remitente:** {row['remitente']}")
                        st.markdown(f"**Tipo:** {row.get('tipo_documento', 'Correo Electrónico')}")
                        st.markdown(f"**Prioridad:** `{row.get('prioridad', 'Normal')}`")
                        st.markdown(f"**Observaciones:** {row['observaciones'] or 'Sin observaciones.'}")
                    with col2:
                        st.markdown(f"**Área Derivada:** `{row['area_derivada']}`")
                        st.markdown(f"**Fecha Derivación:** {row['fecha_derivacion']}")
                        st.markdown(f"**Registrado por:** {row.get('registrado_por', 'Gabinete')}")
                        st.markdown(f"**Tiempo Transcurrido:** {row['Dias_Transcurridos']} día(s)")
                    with col3:
                        if st.button("✅ FINIQUITAR", key=f"fin_{row['id']}", type="primary", use_container_width=True):
                            conn = sqlite3.connect(DB_NAME)
                            c = conn.cursor()
                            c.execute("UPDATE correos SET estado = 'FINIQUITADO', fecha_finiquito = ? WHERE id = ?", (date.today().strftime("%Y-%m-%d"), row['id']))
                            conn.commit()
                            conn.close()
                            df = cargar_datos()
                            st.rerun()
                        if st.button("✏️ Editar", key=f"btn_edit_{row['id']}", use_container_width=True):
                            st.session_state.edit_id = row['id']
                            st.rerun()
                        if st.button("🗑️ Eliminar", key=f"del_{row['id']}", use_container_width=True):
                            conn = sqlite3.connect(DB_NAME)
                            c = conn.cursor()
                            c.execute("DELETE FROM correos WHERE id = ?", (row['id'],))
                            conn.commit()
                            conn.close()
                            df = cargar_datos()
                            st.rerun()
        else:
            st.success("🎉 No existen trámites pendientes.")
    else:
        st.info("No hay trámites registrados aún.")

# TAB 2: REGISTRO DE DERIVACIONES
with tab2:
    st.markdown("##### ➕ Formulario de Ingreso de Correos / Documentos")
    with st.form("form_gabinete", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            remitente = st.text_input("Remitente:")
            asunto = st.text_input("Asunto / Resumen:")
            tipo_documento = st.selectbox("Tipo de Documento:", ["Correo Electrónico", "Nota Oficial", "Nota Externa", "Informe Técnico", "Directiva / Resolución", "Otro"])
            mesa_entrada = st.text_input("Nº Mesa de Entrada / Ref. (Opcional):")
        with col_b:
            area_derivada = st.selectbox("Dirección / Área a la que se deriva:", AREAS_LIST)
            prioridad = st.radio("Prioridad del Trámite:", ["Normal", "Alta", "Baja"], horizontal=True)
            fecha_derivacion = st.date_input("Fecha de Derivación:", value=date.today())
            registrado_por = st.selectbox("Registrado por:", ["Gabinete / Jefatura", "Secretaría de Gabinete", "Asistente Técnico"])
        observaciones = st.text_area("Observaciones o instrucciones:")
        submitted = st.form_submit_button("💾 Registrar y Derivar Trámite", type="primary", use_container_width=True)
        if submitted:
            if remitente.strip() and asunto.strip():
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("""
                    INSERT INTO correos (mesa_entrada, remitente, asunto, tipo_documento, area_derivada, prioridad, registrado_por, fecha_derivacion, estado, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDIENTE', ?)
                """, (mesa_entrada, remitente, asunto, tipo_documento, area_derivada, prioridad, registrado_por, fecha_derivacion.strftime("%Y-%m-%d"), observaciones))
                conn.commit()
                conn.close()
                st.success("✅ **Trámite registrado y derivado exitosamente.**")
                df = cargar_datos()
                st.rerun()
            else:
                st.error("⚠️ Complete los campos obligatorios: **Remitente** y **Asunto**.")

# TAB 3: DASHBOARD POWER BI
with tab3:
    st.markdown("##### 📊 Panel Ejecutivo de Control de Gestión")
    if not df.empty:
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
        
        st.markdown("##### 🎛️ Segmentadores / Filtros de Análisis")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            anos_disponibles = sorted(df_pb["Año"].unique().tolist(), reverse=True)
            f_ano = st.multiselect("🗓️ Año:", options=anos_disponibles, default=anos_disponibles)
        with col_f2:
            df_m = df_pb[df_pb["Año"].isin(f_ano)] if f_ano else df_pb
            meses_ord = df_m.sort_values("Num_Mes")["Nombre_Mes"].unique().tolist()
            f_mes = st.multiselect("📅 Mes:", options=meses_ord, default=meses_ord)
        with col_f3:
            areas_disp = sorted(df_pb["area_derivada"].unique().tolist())
            f_direccion = st.multiselect("🏛️ Dirección:", options=areas_disp, default=areas_disp)
            
        df_dash = df_pb.copy()
        if f_ano: df_dash = df_dash[df_dash["Año"].isin(f_ano)]
        if f_mes: df_dash = df_dash[df_dash["Nombre_Mes"].isin(f_mes)]
        if f_direccion: df_dash = df_dash[df_dash["area_derivada"].isin(f_direccion)]
            
        st.markdown("---")
        if not df_dash.empty:
            total_casos = len(df_dash)
            tot_finiquitados = len(df_dash[df_dash["Estado_Plazo"] == "FINIQUITADO"])
            tot_pendientes = total_casos - tot_finiquitados
            tot_vencidos = len(df_dash[df_dash["Estado_Plazo"] == "VENCIDO"])
            pct_eficiencia = round((tot_finiquitados / total_casos) * 100, 1) if total_casos > 0 else 0
            promedio_dias = round(df_dash[df_dash["estado"] != "FINIQUITADO"]["Dias_Transcurridos"].mean(), 1) if tot_pendientes > 0 else 0
            
            k1, k2, k3, k4, k5 = st.columns(5)
            with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Trámites</div><div class="kpi-value">{total_casos}</div><div class="kpi-subtext">Casos registrados</div></div>', unsafe_allow_html=True)
            with k2: st.markdown(f'<div class="kpi-card kpi-card-success"><div class="kpi-title">Finiquitados</div><div class="kpi-value">{tot_finiquitados}</div><div class="kpi-subtext">{pct_eficiencia}% efectividad</div></div>', unsafe_allow_html=True)
            with k3: st.markdown(f'<div class="kpi-card kpi-card-warning"><div class="kpi-title">Pendientes</div><div class="kpi-value">{tot_pendientes}</div><div class="kpi-subtext">En gestión</div></div>', unsafe_allow_html=True)
            with k4: st.markdown(f'<div class="kpi-card kpi-card-danger"><div class="kpi-title">Vencidos</div><div class="kpi-value">{tot_vencidos}</div><div class="kpi-subtext">> 8 días</div></div>', unsafe_allow_html=True)
            with k5: st.markdown(f'<div class="kpi-card"><div class="kpi-title">Prom. Espera</div><div class="kpi-value">{promedio_dias}</div><div class="kpi-subtext">Días acumulados</div></div>', unsafe_allow_html=True)
                
            st.markdown("---")
            col_chart1, col_chart2 = st.columns([1, 1])
            color_map = {"FINIQUITADO": "#2ea44f", "EN PLAZO": "#2563eb", "SEGUIMIENTO": "#f59e0b", "VENCIDO": "#dc2626"}
            
            with col_chart1:
                st.markdown("###### 🍩 **Distribución por Estado (Gráfico de Dona)**")
                conteo_estados = df_dash["Estado_Plazo"].value_counts().reset_index()
                conteo_estados.columns = ["Estado", "Cantidad"]
                fig_donut = px.pie(conteo_estados, names="Estado", values="Cantidad", hole=0.55, color="Estado", color_discrete_map=color_map)
                fig_donut.update_traces(textposition='outside', textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=2)))
                fig_donut.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20), height=320)
                st.plotly_chart(fig_donut, use_container_width=True)
                
            with col_chart2:
                st.markdown("###### 📊 **Carga de Trámites por Dirección**")
                df_area = df_dash.groupby(["area_derivada", "Estado_Plazo"]).size().reset_index(name="Cantidad")
                fig_bar = px.bar(df_area, y="area_derivada", x="Cantidad", color="Estado_Plazo", orientation="h", color_discrete_map=color_map, barmode="stack")
                fig_bar.update_layout(xaxis_title=None, yaxis_title=None, legend_title_text=None, margin=dict(t=20, b=20, l=10, r=10), height=320)
                st.plotly_chart(fig_bar, use_container_width=True)
                
            st.markdown("---")
            st.markdown("##### 🚨 **TOP 20: Trámites con Mayor Tiempo en Espera**")
            df_sin_finiquitar = df_dash[df_dash["estado"] != "FINIQUITADO"].copy()
            if not df_sin_finiquitar.empty:
                top_20 = df_sin_finiquitar.sort_values(by="Dias_Transcurridos", ascending=False).head(20)
                top_20_display = top_20[["id", "mesa_entrada", "asunto", "remitente", "area_derivada", "prioridad", "fecha_derivacion", "Dias_Transcurridos", "Estado_Plazo"]].copy()
                top_20_display.rename(columns={"id": "ID", "mesa_entrada": "Mesa Entrada", "asunto": "Asunto / Detalle", "remitente": "Remitente", "area_derivada": "Área Responsable", "prioridad": "Prioridad", "fecha_derivacion": "F. Derivación", "Dias_Transcurridos": "Días Acumulados", "Estado_Plazo": "Estado Plazo"}, inplace=True)
                st.dataframe(
                    top_20_display, use_container_width=True, hide_index=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID", format="#%d"),
                        "Días Acumulados": st.column_config.ProgressColumn("Días Acumulados", format="%d días", min_value=0, max_value=max(int(top_20_display["Días Acumulados"].max()), 10))
                    }
                )
            else:
                st.success("🎉 No existen trámites pendientes.")
        else:
            st.warning("⚠️ No se encontraron registros con los filtros seleccionados.")
    else:
        st.info("No hay registros cargados aún.")

# TAB 4: REPORTE COMPLETO
with tab4:
    st.markdown("##### 📋 Base de Datos Consolidada de Gestión")
    if not df.empty:
        df_export = df.copy()
        estados_powerbi, dias_powerbi = [], []
        for _, row in df_export.iterrows():
            st_calc, dias = calcular_estado_automatico(row["fecha_derivacion"], row["estado"])
            estados_powerbi.append(st_calc)
            dias_powerbi.append(dias if row["estado"] != "FINIQUITADO" else 0)
        df_export["Estado_Plazo"] = estados_powerbi
        df_export["Dias_Transcurridos"] = dias_powerbi
        
        st.dataframe(df_export, use_container_width=True)
        st.markdown("---")
        c_down1, c_down2 = st.columns(2)
        with c_down1:
            csv_data = df_export.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 Descargar Base Completa en CSV", data=csv_data, file_name="gestion_gabinete.csv", mime="text/csv", type="primary", use_container_width=True)
        with c_down2:
            buffer = pd.ExcelWriter("reporte_gabinete.xlsx", engine="openpyxl")
            df_export.to_excel(buffer, index=False, sheet_name="Gestion_Gabinete")
            buffer.close()
            with open("reporte_gabinete.xlsx", "rb") as f:
                st.download_button("📊 Descargar Reporte en Excel", data=f, file_name="reporte_gabinete.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    else:
        st.info("No hay registros en la base de datos.")