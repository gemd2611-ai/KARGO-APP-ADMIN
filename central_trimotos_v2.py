import streamlit as st
import textwrap
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
from geopy.geocoders import Nominatim
from supabase import create_client

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Trimotos Delivery | Central",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# ESTILOS - CENTRAL MODERNA
# =========================================================
render_html(
    """
    <style>
    /* ---------- BASE ---------- */
    .stApp {
        background: #F7F8FA;
    }

    [data-testid="stHeader"] {
        background: rgba(247,248,250,0.95);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 0;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] * {
        color: #F9FAFB;
    }

    .brand-box {
        padding: 8px 8px 20px 8px;
        margin-bottom: 12px;
    }

    .brand-icon {
        width: 48px;
        height: 48px;
        border-radius: 15px;
        background: #35D0B1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        margin-bottom: 12px;
    }

    .brand-title {
        font-size: 21px;
        font-weight: 800;
        line-height: 1.1;
        color: #FFFFFF;
    }

    .brand-subtitle {
        color: #9CA3AF;
        font-size: 12px;
        margin-top: 5px;
    }

    .sidebar-section {
        color: #6B7280 !important;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 18px 8px 7px;
    }

    .sidebar-user {
        background: #1F2937;
        border-radius: 16px;
        padding: 13px;
        margin-top: 22px;
        border: 1px solid #374151;
    }

    .sidebar-avatar {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        background: #35D0B1;
        color: #111827;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        margin-right: 9px;
        vertical-align: middle;
    }

    .sidebar-user-name {
        display: inline-block;
        vertical-align: middle;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 13px;
    }

    .sidebar-user-role {
        color: #9CA3AF;
        font-size: 11px;
        margin-left: 49px;
        margin-top: -3px;
    }

    /* ---------- TYPOGRAPHY ---------- */
    .page-kicker {
        color: #35BFA5;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .7px;
        margin-bottom: 4px;
    }

    .page-title {
        color: #111827;
        font-size: 31px;
        font-weight: 800;
        line-height: 1.15;
        margin: 0;
    }

    .page-subtitle {
        color: #6B7280;
        font-size: 14px;
        margin-top: 7px;
        margin-bottom: 24px;
    }

    .section-title {
        color: #111827;
        font-size: 20px;
        font-weight: 800;
        margin-top: 18px;
        margin-bottom: 12px;
    }

    /* ---------- KPI CARDS ---------- */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 18px;
        min-height: 122px;
        box-shadow: 0 5px 18px rgba(17,24,39,.04);
    }

    .kpi-icon {
        width: 42px;
        height: 42px;
        border-radius: 13px;
        background: #E8FBF7;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 21px;
        margin-bottom: 12px;
    }

    .kpi-label {
        color: #6B7280;
        font-size: 12px;
        font-weight: 600;
    }

    .kpi-value {
        color: #111827;
        font-size: 26px;
        font-weight: 800;
        margin-top: 2px;
    }

    /* ---------- TRIP CARDS ---------- */
    .trip-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 5px 18px rgba(17,24,39,.04);
    }

    .trip-card:hover {
        border-color: #C7EDE5;
    }

    .trip-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
    }

    .trip-client {
        color: #111827;
        font-size: 16px;
        font-weight: 800;
    }

    .status-pill {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #FFF7D6;
        color: #8A6700;
        font-size: 11px;
        font-weight: 800;
    }

    .status-pill.done {
        background: #E8FBF7;
        color: #087F6D;
    }

    .route-line {
        color: #4B5563;
        font-size: 13px;
        margin-top: 13px;
        line-height: 1.65;
    }

    .trip-meta {
        color: #6B7280;
        font-size: 12px;
        margin-top: 11px;
    }

    .trip-price {
        color: #0B9E84;
        font-size: 21px;
        font-weight: 800;
        white-space: nowrap;
    }

    /* ---------- INFO BOX ---------- */
    .info-box {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 5px 18px rgba(17,24,39,.04);
        margin-bottom: 16px;
    }

    .info-box-title {
        color: #111827;
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 14px;
    }

    /* ---------- DRIVER CARD ---------- */
    .driver-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(17,24,39,.035);
    }

    .driver-name {
        color: #111827;
        font-size: 15px;
        font-weight: 800;
    }

    .driver-detail {
        color: #6B7280;
        font-size: 12px;
        margin-top: 4px;
    }

    .online-dot {
        color: #10B981;
        font-size: 12px;
        font-weight: 800;
    }

    /* ---------- FORMS ---------- */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        border-radius: 13px !important;
    }

    .stButton > button {
        border-radius: 13px;
        min-height: 42px;
        font-weight: 700;
        border: 1px solid #E5E7EB;
    }

    .stButton > button[kind="primary"] {
        background: #35D0B1;
        border-color: #35D0B1;
        color: #111827;
    }

    /* ---------- MAP ---------- */
    .map-title {
        color: #111827;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    /* ---------- MOBILE ---------- */
    @media (max-width: 900px) {
        .page-title {
            font-size: 25px;
        }

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def render_html(content):
    """Render HTML without accidental Markdown code-block indentation."""
    st.markdown(textwrap.dedent(content).strip(), unsafe_allow_html=True)


# =========================================================
# SUPABASE
# =========================================================
# Recomendado:
# En .streamlit/secrets.toml:
#
# SUPABASE_URL = "https://xxxxx.supabase.co"
# SUPABASE_KEY = "xxxxx"
#
# El fallback solo sirve para mantener compatibilidad con tu
# instalación actual. Se recomienda migrar las credenciales
# fuera del código.
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    SUPABASE_URL = "https://jlurdtdidymjzctryilh.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpsdXJkdGRpZHltanpjdHJ5aWxoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc3NTA5MjUsImV4cCI6MjEwMzMyNjkyNX0.ZaA_AwdoyAU-bt_rmby98ORfAkpvkLhX7XHdrK9D_zE"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================================================
# FUNCIONES
# =========================================================
@st.cache_data(ttl=60)
def cargar_choferes():
    try:
        res = (
            supabase.table("choferes")
            .select("cedula, nombre, moto_marca, moto_modelo, placa, capacidad_kg")
            .execute()
        )
        return res.data or []
    except Exception as e:
        st.error(f"No se pudieron cargar los choferes: {e}")
        return []


@st.cache_data(ttl=30)
def cargar_viajes():
    try:
        res = supabase.table("viajes").select("*").execute()
        return res.data or []
    except Exception as e:
        st.error(f"No se pudieron cargar los viajes: {e}")
        return []


def limpiar_cache():
    cargar_choferes.clear()
    cargar_viajes.clear()


def obtener_datos_ruta(origen_str, destino_str):
    geolocator = Nominatim(user_agent="central_trimotos_caracas")

    try:
        loc_orig = geolocator.geocode(
            origen_str + ", Caracas, Venezuela",
            timeout=10,
        )
        loc_dest = geolocator.geocode(
            destino_str + ", Caracas, Venezuela",
            timeout=10,
        )

        if not loc_orig or not loc_dest:
            return None

        lat1, lon1 = loc_orig.latitude, loc_orig.longitude
        lat2, lon2 = loc_dest.latitude, loc_dest.longitude

        url = (
            "https://router.project-osrm.org/route/v1/driving/"
            f"{lon1},{lat1};{lon2},{lat2}"
            "?overview=full&geometries=geojson"
        )

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        res = response.json()

        if res.get("code") == "Ok" and res.get("routes"):
            ruta = res["routes"][0]

            km = round(ruta["distance"] / 1000, 2)
            puntos = [
                [p[1], p[0]]
                for p in ruta["geometry"]["coordinates"]
            ]

            return {
                "km": km,
                "puntos": puntos,
                "orig": [lat1, lon1],
                "dest": [lat2, lon2],
            }

    except Exception:
        return None

    return None


def calcular_tarifa(km):
    # Mantiene tu fórmula actual:
    # Hasta 3 km = $6
    # Luego + $0.80 por cada km adicional
    return round(6.0 if km <= 3 else 6.0 + ((km - 3) * 0.80), 2)


def iniciales(nombre):
    partes = (nombre or "Administrador").split()
    return "".join([p[0] for p in partes[:2]]).upper()


def obtener_nombre_chofer(cedula, choferes):
    for c in choferes:
        if c.get("cedula") == cedula:
            return c.get("nombre", "Sin asignar")
    return "Sin asignar"


def estado_clase(estatus):
    if estatus == "🟢 Entregado":
        return "done"
    return ""


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    render_html(
        """
        <div class="brand-box">
            <div class="brand-icon">🛵</div>
            <div class="brand-title">TRIMOTOS<br>DELIVERY</div>
            <div class="brand-subtitle">Central de Despacho</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_html('<div class="sidebar-section">Operación</div>', unsafe_allow_html=True)

    menu = st.radio(
        "Navegación",
        [
            "🏠 Inicio",
            "📦 Despachos",
            "🛵 Choferes",
            "🗺️ Mapa en vivo",
            "📸 Entregas",
            "📊 Reportes",
            "⚙️ Configuración",
        ],
        label_visibility="collapsed",
    )

    render_html(
        f"""
        <div class="sidebar-user">
            <span class="sidebar-avatar">GM</span>
            <span class="sidebar-user-name">Gabriel Martínez</span>
            <div class="sidebar-user-role">Administrador</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 Actualizar datos", use_container_width=True):
        limpiar_cache()
        st.rerun()


# =========================================================
# DATOS
# =========================================================
choferes = cargar_choferes()
viajes = cargar_viajes()

viajes_pendientes = [
    v for v in viajes
    if v.get("estatus") == "🟡 En Ruta"
]

viajes_entregados = [
    v for v in viajes
    if v.get("estatus") == "🟢 Entregado"
]

total_hoy = 0.0
hoy = datetime.now().strftime("%Y-%m-%d")

for v in viajes:
    fecha = str(v.get("fecha", ""))
    if fecha.startswith(hoy):
        try:
            total_hoy += float(v.get("total", 0) or 0)
        except Exception:
            pass


# =========================================================
# 🏠 INICIO
# =========================================================
if menu == "🏠 Inicio":
    render_html('<div class="page-kicker">CENTRAL DE DESPACHO</div>', unsafe_allow_html=True)
    render_html('<div class="page-title">¡Hola, Gabriel! 👋</div>', unsafe_allow_html=True)
    render_html(
        '<div class="page-subtitle">Aquí tienes el resumen de la operación de Trimotos Delivery.</div>',
        unsafe_allow_html=True,
    )

    # KPIs
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        render_html(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">📦</div>
                <div class="kpi-label">Despachos pendientes</div>
                <div class="kpi-value">{len(viajes_pendientes)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k2:
        render_html(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">🛵</div>
                <div class="kpi-label">Choferes registrados</div>
                <div class="kpi-value">{len(choferes)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k3:
        render_html(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">✅</div>
                <div class="kpi-label">Entregas realizadas</div>
                <div class="kpi-value">{len(viajes_entregados)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k4:
        render_html(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">💰</div>
                <div class="kpi-label">Ventas de hoy</div>
                <div class="kpi-value">${total_hoy:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_html('<div class="section-title">Despachos recientes</div>', unsafe_allow_html=True)

    recientes = sorted(
        viajes,
        key=lambda x: str(x.get("fecha", "")),
        reverse=True,
    )[:5]

    if not recientes:
        st.info("Todavía no hay despachos registrados.")
    else:
        for v in recientes:
            estatus = v.get("estatus", "Sin estado")
            clase = estado_clase(estatus)
            chofer = obtener_nombre_chofer(v.get("chofer_cedula"), choferes)

            render_html(
                f"""
                <div class="trip-card">
                    <div class="trip-top">
                        <div>
                            <div class="trip-client">
                                🏢 {v.get("comercio", "Particular")}
                            </div>
                            <div class="trip-meta">
                                {v.get("fecha", "")} · 🛵 {chofer}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <span class="status-pill {clase}">{estatus}</span>
                            <div class="trip-price" style="margin-top:8px;">
                                ${float(v.get("total", 0) or 0):.2f}
                            </div>
                        </div>
                    </div>

                    <div class="route-line">
                        📍 <b>{v.get("origen", "N/A")}</b>
                        &nbsp; → &nbsp;
                        🏁 <b>{v.get("destino", "N/A")}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    render_html('<div class="section-title">Acciones rápidas</div>', unsafe_allow_html=True)

    a1, a2, a3 = st.columns(3)

    with a1:
        if st.button("📦 Nuevo despacho", use_container_width=True, type="primary"):
            st.session_state.menu_forzado = "📦 Despachos"
            st.rerun()

    with a2:
        if st.button("🛵 Ver choferes", use_container_width=True):
            st.session_state.menu_forzado = "🛵 Choferes"
            st.rerun()

    with a3:
        if st.button("📊 Ver reportes", use_container_width=True):
            st.session_state.menu_forzado = "📊 Reportes"
            st.rerun()


# =========================================================
# 📦 DESPACHOS
# =========================================================
elif menu == "📦 Despachos":
    render_html('<div class="page-kicker">OPERACIÓN</div>', unsafe_allow_html=True)
    render_html('<div class="page-title">Nuevo despacho 📦</div>', unsafe_allow_html=True)
    render_html(
        '<div class="page-subtitle">Cotiza una ruta y asigna el servicio a un chofer.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        render_html(
            '<div class="info-box-title">Información del servicio</div>',
            unsafe_allow_html=True,
        )

        comercio = st.text_input(
            "Cliente / Comercio",
            value="Ferretería El Ancla",
        )

        origen = st.text_input(
            "Origen",
            value="Quinta Crespo",
        )

        destino = st.text_input(
            "Destino",
            value="Chacao",
        )

        categoria = st.selectbox(
            "Categoría de carga",
            [
                "Cat A (Hasta 150 kg)",
                "Cat B (Hasta 450 kg)",
            ],
        )

        if st.button(
            "🗺️ Calcular ruta",
            use_container_width=True,
            type="primary",
        ):
            if not origen or not destino:
                st.warning("Indica el origen y destino.")
            else:
                with st.spinner("Calculando ruta..."):
                    ruta = obtener_datos_ruta(origen, destino)

                if ruta:
                    st.session_state.ruta_activa = ruta
                    st.session_state.datos_cotizacion = {
                        "comercio": comercio,
                        "origen": origen,
                        "destino": destino,
                        "categoria": categoria,
                    }
                    st.success("Ruta calculada correctamente.")
                else:
                    st.error(
                        "No fue posible calcular la ruta. "
                        "Verifica las direcciones e intenta nuevamente."
                    )

    with right:
        render_html(
            '<div class="info-box-title">Resumen de cotización</div>',
            unsafe_allow_html=True,
        )

        if "ruta_activa" not in st.session_state:
            st.info("Calcula una ruta para ver la cotización.")
        else:
            ruta = st.session_state.ruta_activa
            datos = st.session_state.get("datos_cotizacion", {})

            km = ruta["km"]
            total = calcular_tarifa(km)

            c1, c2 = st.columns(2)

            with c1:
                st.metric("Distancia", f"{km:.2f} km")

            with c2:
                st.metric("Total carrera", f"${total:.2f}")

            render_html("---")

            st.write("**Asignar chofer**")

            if choferes:
                opciones = {
                    f"{c.get('nombre', 'Sin nombre')} · "
                    f"{c.get('moto_marca', 'Moto')} "
                    f"{c.get('moto_modelo', '')} · "
                    f"CI: {c.get('cedula', '')}": c.get("cedula")
                    for c in choferes
                }

                seleccion = st.selectbox(
                    "Selecciona el chofer",
                    list(opciones.keys()),
                )

                cedula_asig = opciones[seleccion]

                if st.button(
                    "🚀 Asignar y enviar despacho",
                    use_container_width=True,
                    type="primary",
                ):
                    nuevo_viaje = {
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "comercio": datos.get("comercio", comercio),
                        "origen": datos.get("origen", origen),
                        "destino": datos.get("destino", destino),
                        "total": total,
                        "chofer_cedula": cedula_asig,
                        "estatus": "🟡 En Ruta",
                    }

                    try:
                        supabase.table("viajes").insert(nuevo_viaje).execute()
                        limpiar_cache()
                        st.success(
                            "¡Despacho creado! El servicio ya está disponible "
                            "para el chofer."
                        )
                        st.session_state.pop("ruta_activa", None)
                        st.session_state.pop("datos_cotizacion", None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"No fue posible crear el despacho: {e}")
            else:
                st.warning(
                    "No hay choferes registrados. Registra al menos uno "
                    "antes de asignar un despacho."
                )

    # MAPA
    if "ruta_activa" in st.session_state:
        render_html('<div class="section-title">Vista de ruta</div>', unsafe_allow_html=True)

        r = st.session_state.ruta_activa

        mapa = folium.Map(
            location=r["orig"],
            zoom_start=13,
            tiles="CartoDB positron",
        )

        folium.Marker(
            r["orig"],
            tooltip="Origen",
            popup="📍 Origen",
            icon=folium.Icon(color="green", icon="home"),
        ).add_to(mapa)

        folium.Marker(
            r["dest"],
            tooltip="Destino",
            popup="🏁 Destino",
            icon=folium.Icon(color="red", icon="flag"),
        ).add_to(mapa)

        folium.PolyLine(
            r["puntos"],
            color="#35CDB0",
            weight=6,
            opacity=0.9,
        ).add_to(mapa)

        st_folium(
            mapa,
            width=None,
            height=450,
            use_container_width=True,
        )

    # DESPACHOS ACTUALES
    render_html('<div class="section-title">Despachos pendientes</div>', unsafe_allow_html=True)

    if not viajes_pendientes:
        st.info("No existen despachos pendientes.")
    else:
        for v in sorted(
            viajes_pendientes,
            key=lambda x: str(x.get("fecha", "")),
            reverse=True,
        ):
            chofer = obtener_nombre_chofer(v.get("chofer_cedula"), choferes)

            render_html(
                f"""
                <div class="trip-card">
                    <div class="trip-top">
                        <div>
                            <div class="trip-client">🏢 {v.get("comercio", "Particular")}</div>
                            <div class="trip-meta">🛵 {chofer} · {v.get("fecha", "")}</div>
                        </div>
                        <div class="trip-price">${float(v.get("total", 0) or 0):.2f}</div>
                    </div>
                    <div class="route-line">
                        📍 {v.get("origen", "N/A")}
                        &nbsp; → &nbsp;
                        🏁 {v.get("destino", "N/A")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# 🛵 CHOFERES
# =========================================================
elif menu == "🛵 Choferes":
    render_html('<div class="page-kicker">EQUIPO</div>', unsafe_allow_html=True)
    render_html('<div class="page-title">Choferes 🛵</div>', unsafe_allow_html=True)
    render_html(
        '<div class="page-subtitle">Gestiona los conductores registrados en la operación.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("➕ Registrar nuevo chofer", expanded=False):
        with st.form("form_chofer"):
            c1, c2 = st.columns(2)

            with c1:
                cedula = st.text_input("Cédula de identidad", "V-20123456")
                nombre = st.text_input("Nombre completo", "Carlos Pérez")
                clave = st.text_input("Contraseña de acceso", "1234", type="password")

            with c2:
                marca = st.text_input("Marca de moto", "Bera")
                modelo = st.text_input("Modelo", "SBR 150")
                placa = st.text_input("Placa", "AB1C23D")
                capacidad = st.number_input(
                    "Capacidad de carga (kg)",
                    min_value=1,
                    value=150,
                )

            guardar = st.form_submit_button(
                "💾 Guardar chofer",
                use_container_width=True,
            )

            if guardar:
                datos = {
                    "cedula": cedula.strip(),
                    "nombre": nombre.strip(),
                    "clave": clave,
                    "moto_marca": marca.strip(),
                    "moto_modelo": modelo.strip(),
                    "placa": placa.strip(),
                    "capacidad_kg": capacidad,
                }

                if not cedula or not nombre or not clave:
                    st.warning("Cédula, nombre y contraseña son obligatorios.")
                else:
                    try:
                        supabase.table("choferes").upsert(datos).execute()
                        limpiar_cache()
                        st.success("Chofer registrado correctamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"No fue posible guardar el chofer: {e}")

    render_html('<div class="section-title">Choferes registrados</div>', unsafe_allow_html=True)

    if not choferes:
        st.info("No hay choferes registrados.")
    else:
        cols = st.columns(2)

        for i, c in enumerate(choferes):
            with cols[i % 2]:
                nombre = c.get("nombre", "Sin nombre")
                activos = [
                    v for v in viajes_pendientes
                    if v.get("chofer_cedula") == c.get("cedula")
                ]

                render_html(
                    f"""
                    <div class="driver-card">
                        <div class="online-dot">● ACTIVO EN SISTEMA</div>
                        <div class="driver-name">🛵 {nombre}</div>
                        <div class="driver-detail">
                            🪪 CI: {c.get("cedula", "")}
                        </div>
                        <div class="driver-detail">
                            🛵 {c.get("moto_marca", "Moto")} {c.get("moto_modelo", "")}
                            · 🏷️ {c.get("placa", "Sin placa")}
                        </div>
                        <div class="driver-detail">
                            📦 Capacidad: {c.get("capacidad_kg", 0)} kg
                            · 📦 Servicios pendientes: {len(activos)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# =========================================================
# 🗺️ MAPA EN VIVO
# =========================================================
elif menu == "🗺️ Mapa en vivo":
    render_html('<div class="page-kicker">MONITOREO</div>', unsafe_allow_html=True)
    render_html('<div class="page-title">Mapa en vivo 🗺️</div>', unsafe_allow_html=True)
    render_html(
        '<div class="page-subtitle">Vista de los servicios registrados y sus rutas.</div>',
        unsafe_allow_html=True,
    )

    if "ruta_activa" in st.session_state:
        r = st.session_state.ruta_activa

        mapa = folium.Map(
            location=r["orig"],
            zoom_start=12,
            tiles="CartoDB positron",
        )

        folium.Marker(
            r["orig"],
            tooltip="Origen",
            icon=folium.Icon(color="green"),
        ).add_to(mapa)

        folium.Marker(
            r["dest"],
            tooltip="Destino",
            icon=folium.Icon(color="red"),
        ).add_to(mapa)

        folium.PolyLine(
            r["puntos"],
            color="#35CDB0",
            weight=6,
        ).add_to(mapa)

        st_folium(mapa, width=None, height=600, use_container_width=True)

        st.caption(
            "Actualmente el mapa muestra la última ruta calculada. "
            "El seguimiento GPS de choferes puede agregarse en una siguiente etapa."
        )
    else:
        st.info(
            "No hay una ruta activa en esta sesión. "
            "Calcula una ruta desde Despachos para visualizarla aquí."
        )

    render_html('<div class="section-title">Estado de la operación</div>', unsafe_allow_html=True)

    activos = [
        v for v in viajes
        if v.get("estatus") == "🟡 En Ruta"
    ]

    if activos:
        for v in activos:
            chofer = obtener_nombre_chofer(v.get("chofer_cedula"), choferes)

            render_html(
                f"""
                <div class="trip-card">
                    <div class="trip-top">
                        <div>
                            <div class="trip-client">🟡 {v.get("comercio", "Particular")}</div>
                            <div class="trip-meta">🛵 {chofer}</div>
                        </div>
                        <div class="trip-price">${float(v.get("total", 0) or 0):.2f}</div>
                    </div>
                    <div class="route-line">
                        📍 {v.get("origen", "N/A")} → 🏁 {v.get("destino", "N/A")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("No hay servicios pendientes en este momento.")


# =========================================================
# 📸 ENTREGAS
# =========================================================
elif menu == "📸 Entregas":
    render_html('<div class="page-kicker">COMPROBANTES</div>', unsafe_allow_html=True)
    render_html('<div class="page-title">Entregas 📸</div>', unsafe_allow_html=True)
    render_html(
        '<div class="page-subtitle">Consulta las entregas realizadas y sus comprobantes.</div>',
        unsafe_allow_html=True,
    )

    if not viajes_entregados:
        st.info("Todavía no hay entregas completadas.")
    else:
        for v in sorted(
            viajes_entregados,
            key=lambda x: str(x.get("fecha", "")),
            reverse=True,
        ):
            chofer = obtener_nombre_chofer(v.get("chofer_cedula"), choferes)

            render_html(
                f"""
                <div class="trip-card">
                    <div class="trip-top">
                        <div>
                            <div class="trip-client">🟢 {v.get("comercio", "Particular")}</div>
                            <div class="trip-meta">
                                🛵 {chofer} · {v.get("fecha", "")}
                            </div>
                        </div>
                        <div class="trip-price">${float(v.get("total", 0) or 0):.2f}</div>
                    </div>
                    <div class="route-line">
                        📍 {v.get("origen", "N/A")} → 🏁 {v.get("destino", "N/A")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if v.get("foto_base64"):
                with st.expander(f"🖼️ Ver comprobante · Viaje #{v.get('id', '')}"):
                    st.image(
                        v["foto_base64"],
                        caption="Comprobante de entrega",
                        use_container_width=True,
                    )
            else:
                st.caption("Este viaje no tiene comprobante fotográfico.")


# =========================================================
# 📊 REPORTES
# =========================================================
elif menu == "📊 Reportes":
    render_html('<div class="page-kicker">ANÁLISIS</div>', unsafe_allow_html=True)
    render_html('<div class="page-title">Reportes 📊</div>', unsafe_allow_html=True)
    render_html(
        '<div class="page-subtitle">Resumen de la operación registrada en Supabase.</div>',
        unsafe_allow_html=True,
    )

    total_viajes = len(viajes)
    total_entregados = len(viajes_entregados)
    total_pendientes = len(viajes_pendientes)

    ingreso_total = 0.0
    ingreso_entregado = 0.0

    for v in viajes:
        try:
            monto = float(v.get("total", 0) or 0)
        except Exception:
            monto = 0.0

        ingreso_total += monto

        if v.get("estatus") == "🟢 Entregado":
            ingreso_entregado += monto

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.metric("Total viajes", total_viajes)

    with r2:
        st.metric("Entregados", total_entregados)

    with r3:
        st.metric("Pendientes", total_pendientes)

    with r4:
        st.metric("Ingresos registrados", f"${ingreso_total:.2f}")

    render_html('<div class="section-title">Detalle de viajes</div>', unsafe_allow_html=True)

    if viajes:
        filas = []

        for v in viajes:
            filas.append(
                {
                    "ID": v.get("id"),
                    "Fecha": v.get("fecha"),
                    "Cliente": v.get("comercio"),
                    "Origen": v.get("origen"),
                    "Destino": v.get("destino"),
                    "Chofer": obtener_nombre_chofer(
                        v.get("chofer_cedula"),
                        choferes,
                    ),
                    "Estado": v.get("estatus"),
                    "Total": float(v.get("total", 0) or 0),
                }
            )

        df = pd.DataFrame(filas)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Descargar reporte CSV",
            data=csv,
            file_name=f"reporte_trimotos_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay datos para generar el reporte.")


# =========================================================
# ⚙️ CONFIGURACIÓN
# =========================================================
elif menu == "⚙️ Configuración":
    render_html('<div class="page-kicker">SISTEMA</div>', unsafe_allow_html=True)
    render_html('<div class="page-title">Configuración ⚙️</div>', unsafe_allow_html=True)
    render_html(
        '<div class="page-subtitle">Parámetros básicos de la Central de Despacho.</div>',
        unsafe_allow_html=True,
    )

    render_html(
        """
        <div class="info-box">
            <div class="info-box-title">💰 Fórmula actual de tarifa</div>
            <div style="color:#6B7280; font-size:13px; line-height:1.7;">
                Hasta 3 km: <b>$6.00</b><br>
                Cada km adicional: <b>$0.80</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "La fórmula de tarifa todavía está definida directamente en el código. "
        "En una siguiente etapa podemos llevarla a Supabase para modificarla "
        "desde esta pantalla sin tocar Python."
    )

    render_html(
        """
        <div class="info-box">
            <div class="info-box-title">🔐 Seguridad</div>
            <div style="color:#6B7280; font-size:13px; line-height:1.7;">
                Se recomienda guardar SUPABASE_URL y SUPABASE_KEY en
                <b>.streamlit/secrets.toml</b> y no directamente en el código.
                También recomendamos migrar el login de choferes a Supabase Auth
                en una siguiente fase.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_html(
        """
        <div class="info-box">
            <div class="info-box-title">🛵 Trimotos Delivery</div>
            <div style="color:#6B7280; font-size:13px;">
                Central de Despacho · Versión de interfaz 2.0
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
