import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
from geopy.geocoders import Nominatim
from supabase import create_client

st.set_page_config(page_title="Central de Despacho Pro", layout="wide", page_icon="💻")

# --- CONEXIÓN A NUBE (SUPABASE) ---
SUPABASE_URL = "https://jlurdtdidymjzctryilh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpsdXJkdGRpZHltanpjdHJ5aWxoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc3NTA5MjUsImV4cCI6MjEwMzMyNjkyNX0.ZaA_AwdoyAU-bt_rmby98ORfAkpvkLhX7XHdrK9D_zE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- MOTOR DE MAPA ---
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

menu = st.sidebar.radio("Menú Central", ["📍 Cotizar y Despachar", "🛵 Registrar Choferes", "📊 Historial y Fotos"])

# ==========================================
# 📍 MÓDULO 1: COTIZAR Y DESPACHAR
# ==========================================
if menu == "📍 Cotizar y Despachar":
    st.title("📍 Despacho Central")
    col1, col2 = st.columns(2)
    
    # Cargar choferes registrados desde la nube
    res_ch = supabase.table("choferes").select("cedula, nombre, moto_modelo").execute()
    choferes_db = res_ch.data
    chofer_opts = {f"{c['nombre']} ({c['moto_modelo']}) - CI: {c['cedula']}": c['cedula'] for c in choferes_db}
    
    with col1:
        comercio = st.text_input("Cliente / Comercio", "Ferretería El Ancla")
        origen = st.text_input("Origen", "Quinta Crespo")
        destino = st.text_input("Destino", "Chacao")
        categoria = st.selectbox("Categoría Carga", ["Cat A (Hasta 150 kg)", "Cat B (Hasta 450 kg)"])
        
        if st.button("🗺️ Calcular Ruta", use_container_width=True):
            st.session_state.ruta_activa = obtener_datos_ruta(origen, destino)

    with col2:
        if "ruta_activa" in st.session_state and st.session_state.ruta_activa:
            info = st.session_state.ruta_activa
            km = info["km"]
            total = round(6.0 if km <= 3 else 6.0 + ((km - 3) * 0.80), 2)
            
            st.metric("Distancia", f"{km} km")
            st.metric("Total Carrera", f"${total}")
            
            if chofer_opts:
                chofer_sel = st.selectbox("Asignar Chofer Registrado:", list(chofer_opts.keys()))
                cedula_asig = chofer_opts[chofer_sel]
                
                if st.button("🚀 Asignar y Enviar al Teléfono del Chofer", use_container_width=True):
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

    if "ruta_activa" in st.session_state and st.session_state.ruta_activa:
        r = st.session_state.ruta_activa
        m = folium.Map(location=r["orig"], zoom_start=13)
        folium.Marker(r["orig"], tooltip="Origen", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(r["dest"], tooltip="Destino", icon=folium.Icon(color="red")).add_to(m)
        folium.PolyLine(r["puntos"], color="#0066FF", weight=5).add_to(m)
        st_folium(m, width=1100, height=400)

# ==========================================
# 🛵 MÓDULO 2: GESTIÓN DE CHOFERES
# ==========================================
elif menu == "🛵 Registrar Choferes":
    st.title("🛵 Registro de Choferes")
    
    with st.form("form_chofer"):
        c1, c2 = st.columns(2)
        with c1:
            cedula = st.text_input("Cédula de Identidad (ID Único)", "V-20123456")
            nombre = st.text_input("Nombre Completo", "Carlos Pérez")
            clave = st.text_input("Contraseña de Acceso", "1234")
        with c2:
            marca = st.text_input("Marca de Moto", "Bera")
            modelo = st.text_input("Modelo", "SBR 150")
            placa = st.text_input("Placa", "AB1C23D")
            capacidad = st.number_input("Capacidad de Carga (kg)", value=150)
            
        if st.form_submit_button("💾 Guardar Chofer en Nube"):
            datos = {"cedula": cedula, "nombre": nombre, "clave": clave, "moto_marca": marca, "moto_modelo": modelo, "placa": placa, "capacidad_kg": capacidad}
            supabase.table("choferes").upsert(datos).execute()
            st.success("Chofer registrado con éxito.")

    st.subheader("📋 Lista de Choferes Registrados")
    res = supabase.table("choferes").select("*").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data)[["cedula", "nombre", "moto_marca", "moto_modelo", "placa", "capacidad_kg", "clave"]])

# ==========================================
# 📊 MÓDULO 3: HISTORIAL
# ==========================================
elif menu == "📊 Historial y Fotos":
    st.title("📊 Control de Entregas")
    viajes = supabase.table("viajes").select("*").execute().data
    for v in reversed(viajes):
        with st.expander(f"{v['estatus']} | {v['comercio']} | Total: ${v['total']}"):
            st.write(f"**Chofer Cédula:** {v['chofer_cedula']} | **Fecha:** {v['fecha']}")
            st.write(f"**Ruta:** {v['origen']} ➡️ {v['destino']}")
            if v.get("foto_base64"):
                st.image(v["foto_base64"], caption="Comprobante de Entrega", width=300)