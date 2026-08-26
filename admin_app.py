import streamlit as st
import requests
import folium
import html
from streamlit_folium import st_folium
from datetime import datetime
from geopy.geocoders import Nominatim
from supabase import create_client

st.set_page_config(page_title="Central de Despacho Pro", layout="wide", page_icon="🛵")

# --- CONEXIÓN A NUBE (SUPABASE) ---
SUPABASE_URL = "https://jlurdtdidymjzctryilh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpsdXJkdGRpZHltanpjdHJ5aWxoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc3NTA5MjUsImV4cCI6MjEwMzMyNjkyNX0.ZaA_AwdoyAU-bt_rmby98ORfAkpvkLhX7XHdrK9D_zE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 🎨 ESTILOS — tema inspirado en apps de despacho tipo Ridery
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, .stApp {
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 {
    font-family: 'Poppins', sans-serif;
    color: #1E2749;
    font-weight: 700;
}

.stApp {
    background-color: #F5F7FA;
}

.block-container {
    max-width: 1150px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

#MainMenu, footer, [data-testid="stToolbar"] {
    visibility: hidden;
}

.app-greeting {
    font-family: 'Poppins', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: #1E2749;
    margin-bottom: 0.1rem;
}
.app-subgreeting {
    color: #8A93A6;
    font-size: 1rem;
    margin-bottom: 1.3rem;
}

/* Botones */
button[data-testid="baseButton-primary"] {
    font-family: 'Poppins', sans-serif;
    background-color: #1FD1A8;
    color: white !important;
    border-radius: 14px;
    border: none;
    font-weight: 600;
    padding: 0.6rem 1.2rem;
}
button[data-testid="baseButton-primary"]:hover {
    background-color: #17B892;
    color: white !important;
}
button[data-testid="baseButton-secondary"] {
    font-family: 'Poppins', sans-serif;
    background-color: white;
    color: #1E2749 !important;
    border-radius: 14px;
    border: 1px solid #E4E8EE;
    font-weight: 600;
    padding: 0.6rem 1.2rem;
}
button[data-testid="baseButton-secondary"]:hover {
    border-color: #1FD1A8;
    color: #1FD1A8 !important;
}

/* Inputs tipo píldora */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    border-radius: 22px;
    border: 1px solid #E4E8EE;
    padding: 0.55rem 1.1rem;
    background-color: #FAFBFC;
}
div[data-testid="stSelectbox"] > div > div {
    border-radius: 22px;
}

/* Tarjetas de métricas */
[data-testid="stMetric"], [data-testid="metric-container"] {
    background-color: white;
    border-radius: 18px;
    padding: 1rem 1.2rem;
    box-shadow: 0 4px 16px rgba(15,23,42,0.06);
}

/* Contenedores con borde nativo (st.container(border=True)) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    border: 1px solid #E4E8EE !important;
    box-shadow: 0 4px 16px rgba(15,23,42,0.06);
}

/* Formularios */
[data-testid="stForm"] {
    background-color: white;
    border-radius: 18px;
    padding: 1.5rem;
    box-shadow: 0 4px 16px rgba(15,23,42,0.06);
    border: none;
}

/* Expanders (historial) */
[data-testid="stExpander"] {
    border-radius: 16px;
    border: 1px solid #E4E8EE;
    box-shadow: 0 2px 10px rgba(15,23,42,0.04);
    overflow: hidden;
}

/* Mapa */
iframe {
    border-radius: 18px;
}

/* Tarjeta genérica de estado vacío */
.card {
    background-color: white;
    border-radius: 18px;
    padding: 1.3rem 1.4rem;
    box-shadow: 0 4px 16px rgba(15,23,42,0.06);
}

/* Tarjeta de chofer */
.driver-card {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    background-color: white;
    border-radius: 16px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 2px 10px rgba(15,23,42,0.05);
    margin-bottom: 0.7rem;
}
.driver-icon {
    font-size: 1.6rem;
    background-color: #E9FBF5;
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    flex-shrink: 0;
}
.driver-name {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    color: #1E2749;
    font-size: 1.02rem;
}
.driver-sub {
    color: #8A93A6;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# ⚙️ FUNCIONES
# ==========================================
def obtener_datos_ruta(origen_str, destino_str):
    geolocator = Nominatim(user_agent="central_trimotos_caracas")
    try:
        loc_orig = geolocator.geocode(origen_str + ", Caracas, Venezuela")
        loc_dest = geolocator.geocode(destino_str + ", Caracas, Venezuela")
        if loc_orig and loc_dest:
            lat1, lon1 = loc_orig.latitude, loc_orig.longitude
            lat2, lon2 = loc_dest.latitude, loc_dest.longitude
            url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
            res = requests.get(url, timeout=5).json()
            if res.get("code") == "Ok":
                km = round(res["routes"][0]["distance"] / 1000.0, 2)
                puntos = [[p[1], p[0]] for p in res["routes"][0]["geometry"]["coordinates"]]
                return {"km": km, "puntos": puntos, "orig": [lat1, lon1], "dest": [lat2, lon2]}
    except:
        pass
    return None


def color_estatus(estatus):
    e = estatus.lower()
    if "🟡" in estatus or "ruta" in e:
        return "#F5A623"
    if "✅" in estatus or "entreg" in e:
        return "#1FD1A8"
    if "🔴" in estatus or "cancel" in e:
        return "#E74C3C"
    return "#9AA0A6"


# ==========================================
# 🧭 ENCABEZADO Y NAVEGACIÓN
# ==========================================
if "menu" not in st.session_state:
    st.session_state.menu = "despacho"

st.markdown('<div class="app-greeting">¿Qué despachamos hoy?</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subgreeting">Centro de Despacho · Choferes y entregas</div>', unsafe_allow_html=True)

nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("📍 Despachar", use_container_width=True,
                 type="primary" if st.session_state.menu == "despacho" else "secondary"):
        st.session_state.menu = "despacho"
        st.rerun()
with nav2:
    if st.button("🛵 Choferes", use_container_width=True,
                 type="primary" if st.session_state.menu == "choferes" else "secondary"):
        st.session_state.menu = "choferes"
        st.rerun()
with nav3:
    if st.button("📊 Historial", use_container_width=True,
                 type="primary" if st.session_state.menu == "historial" else "secondary"):
        st.session_state.menu = "historial"
        st.rerun()

st.write("")

# ==========================================
# 📍 MÓDULO 1: COTIZAR Y DESPACHAR
# ==========================================
if st.session_state.menu == "despacho":
    res_ch = supabase.table("choferes").select("cedula, nombre, moto_modelo").execute()
    choferes_db = res_ch.data
    chofer_opts = {f"{c['nombre']} ({c['moto_modelo']}) - CI: {c['cedula']}": c['cedula'] for c in choferes_db}

    res_estatus = supabase.table("viajes").select("estatus").execute().data
    en_ruta = len([v for v in res_estatus if "ruta" in v.get("estatus", "").lower()])

    stat1, stat2 = st.columns(2)
    with stat1:
        st.metric("🛵 Choferes registrados", len(choferes_db))
    with stat2:
        st.metric("🟡 Viajes en ruta", en_ruta)

    st.write("")
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            comercio = st.text_input("Cliente / Comercio", "Ferretería El Ancla")
            origen = st.text_input("📍 Origen", "Quinta Crespo")
            destino = st.text_input("🎯 Destino", "Chacao")
            categoria = st.selectbox("Categoría Carga", ["Cat A (Hasta 150 kg)", "Cat B (Hasta 450 kg)"])
            if st.button("🗺️ Calcular Ruta", use_container_width=True, type="primary"):
                st.session_state.ruta_activa = obtener_datos_ruta(origen, destino)

    with col2:
        if "ruta_activa" in st.session_state and st.session_state.ruta_activa:
            info = st.session_state.ruta_activa
            km = info["km"]
            total = round(6.0 if km <= 3 else 6.0 + ((km - 3) * 0.80), 2)

            m1, m2 = st.columns(2)
            with m1:
                st.metric("Distancia", f"{km} km")
            with m2:
                st.metric("Total Carrera", f"${total}")

            if chofer_opts:
                chofer_sel = st.selectbox("Asignar Chofer Registrado:", list(chofer_opts.keys()))
                cedula_asig = chofer_opts[chofer_sel]

                if st.button("🚀 Asignar y Enviar al Teléfono del Chofer", use_container_width=True, type="primary"):
                    nuevo_viaje = {
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "comercio": comercio,
                        "origen": origen,
                        "destino": destino,
                        "total": total,
                        "chofer_cedula": cedula_asig,
                        "estatus": "🟡 En Ruta"
                    }
                    supabase.table("viajes").insert(nuevo_viaje).execute()
                    st.success("¡Despacho enviado a la app móvil del chofer!")
            else:
                st.warning("Primero debes registrar choferes en el menú lateral.")
        else:
            st.markdown(
                '<div class="card" style="text-align:center; color:#8A93A6; padding:2.6rem 1rem;">'
                '🗺️<br><br>Calcula una ruta para ver el precio<br>y asignar un chofer</div>',
                unsafe_allow_html=True
            )

    if "ruta_activa" in st.session_state and st.session_state.ruta_activa:
        r = st.session_state.ruta_activa
        m = folium.Map(location=r["orig"], zoom_start=13)
        folium.Marker(r["orig"], tooltip="Origen", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(r["dest"], tooltip="Destino", icon=folium.Icon(color="red")).add_to(m)
        folium.PolyLine(r["puntos"], color="#1FD1A8", weight=5).add_to(m)
        st.write("")
        st_folium(m, width=1100, height=400)

# ==========================================
# 🛵 MÓDULO 2: GESTIÓN DE CHOFERES
# ==========================================
elif st.session_state.menu == "choferes":
    st.subheader("🛵 Registro de Choferes")

    with st.form("form_chofer"):
        c1, c2 = st.columns(2)
        with c1:
            cedula = st.text_input("Cédula de Identidad (ID Único)", "V-20123456")
            nombre = st.text_input("Nombre Completo", "Carlos Pérez")
            clave = st.text_input("Contraseña de Acceso", "1234", type="password")
        with c2:
            marca = st.text_input("Marca de Moto", "Bera")
            modelo = st.text_input("Modelo", "SBR 150")
            placa = st.text_input("Placa", "AB1C23D")
            capacidad = st.number_input("Capacidad de Carga (kg)", value=150)

        if st.form_submit_button("💾 Guardar Chofer en Nube", type="primary", use_container_width=True):
            datos = {"cedula": cedula, "nombre": nombre, "clave": clave, "moto_marca": marca,
                     "moto_modelo": modelo, "placa": placa, "capacidad_kg": capacidad}
            supabase.table("choferes").upsert(datos).execute()
            st.success("Chofer registrado con éxito.")

    st.write("")
    st.subheader("📋 Choferes Registrados")
    res = supabase.table("choferes").select("*").execute()
    if res.data:
        for c in res.data:
            st.markdown(f"""
            <div class="driver-card">
                <div class="driver-icon">🛵</div>
                <div>
                    <div class="driver-name">{html.escape(str(c.get('nombre', '')))}</div>
                    <div class="driver-sub">{html.escape(str(c.get('moto_marca', '')))} {html.escape(str(c.get('moto_modelo', '')))} · Placa {html.escape(str(c.get('placa', '')))}</div>
                    <div class="driver-sub">CI: {html.escape(str(c.get('cedula', '')))} · Capacidad: {html.escape(str(c.get('capacidad_kg', '')))} kg</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aún no hay choferes registrados.")

# ==========================================
# 📊 MÓDULO 3: HISTORIAL
# ==========================================
elif st.session_state.menu == "historial":
    st.subheader("📊 Control de Entregas")
    viajes = supabase.table("viajes").select("*").execute().data
    if not viajes:
        st.info("Todavía no hay viajes registrados.")
    for v in reversed(viajes):
        with st.expander(f"{v['estatus']} | {v['comercio']} | Total: ${v['total']}"):
            color = color_estatus(v['estatus'])
            st.markdown(
                f'<span style="background:{color}22; color:{color}; padding:4px 14px; '
                f'border-radius:20px; font-weight:600; font-size:0.85rem;">{html.escape(v["estatus"])}</span>',
                unsafe_allow_html=True
            )
            st.write("")
            st.write(f"**Chofer Cédula:** {v['chofer_cedula']} | **Fecha:** {v['fecha']}")
            st.write(f"**Ruta:** {v['origen']} ➡️ {v['destino']}")
            if v.get("foto_base64"):
                st.image(v["foto_base64"], caption="Comprobante de Entrega", width=300)