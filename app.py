import streamlit as st
import os
import pandas as pd
from datetime import datetime, date, timedelta
import pytz
from supabase import create_client, Client

# Configuración de la página optimizada para dispositivos móviles
st.set_page_config(
    page_title="Gestión Avícola",
    page_icon="🐔",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS avanzados blindados contra el Modo Noche y forzados por ID exacto de Streamlit
st.markdown("""
<style>
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; height: 0px !important; padding: 0px !important; }
    footer { visibility: hidden; }

    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    div[data-testid="stVerticalBlock"] > div:first-child { margin-top: 0px !important; padding-top: 0px !important; }
    
    /* Forzar fondo claro general en la app */
    .stApp { background-color: #f8fafc !important; color: #1e293b !important; }
    
    /* Contenedor tipo tarjeta central */
    .main-card {
        background-color: #ffffff !important;
        padding: 24px;
        border-radius: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border: 1px solid #f1f5f9;
        color: #1e293b !important;
    }
    
    .menu-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .badge-op {
        background-color: #dcfce7 !important; color: #166534 !important; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 14px;
    }
    
    .header-title { color: #0f172a !important; font-size: 24px; font-weight: 700; text-align: center; margin-bottom: 4px; }
    .header-subtitle { color: #64748b !important; font-size: 14px; text-align: center; margin-bottom: 24px; }
    
    /* Estilo de los Banners de tu foto */
    .section-banner-color {
        background-color: #fef3c7 !important; color: #92400e !important; padding: 12px; border-radius: 14px;
        font-weight: bold; font-size: 16px; text-align: center; margin: 20px 0 10px 0; border: 1px solid #fde68a;
    }
    .section-banner-blanco {
        background-color: #f1f5f9 !important; color: #334155 !important; padding: 12px; border-radius: 14px;
        font-weight: bold; font-size: 16px; text-align: center; margin: 25px 0 10px 0; border: 1px solid #e2e8f0;
    }
    
    .totales-container { display: flex; gap: 10px; margin-bottom: 15px; margin-top: 10px; }
    .total-box { flex: 1; padding: 12px 8px; border-radius: 12px; text-align: center; border: 1px solid #e2e8f0; }
    .val-box { font-size: 18px; font-weight: 700; margin-top: 2px; }
    .lbl-box { font-size: 11px; font-weight: 600; text-transform: uppercase; }
    
    div[data-baseweb="select"], div[data-baseweb="input"] { border-radius: 10px; }
    
    label, p, span, div { color: #1e293b !important; }
    .stMarkdown p { color: #1e293b !important; }
    
    /* ➔ ESTILO DE BOTONES BASE (Estilo tarjetas del menú principal) */
    div[data-testid="stButton"] > button {
        background-color: #ffffff !important; color: #1e293b !important; border: 1px solid #e2e8f0 !important;
        padding: 18px 20px !important; border-radius: 14px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        font-size: 16px !important; font-weight: 600 !important; text-align: left !important;
        display: flex !important; justify-content: space-between !important; align-items: center !important; margin-bottom: 12px !important;
        width: 100% !important;
    }
    div[data-testid="stButton"] > button:hover { border-color: #cbd5e1 !important; background-color: #f8fafc !important; }
    
    /* 🔴 ENVOLTURA PARA FORZAR EL BOTÓN EN ROJO (Ver Inventario) */
    .contenedor-rojo div[data-testid="stButton"] > button {
        background-color: #be123c !important; color: white !important; border: none !important;
        text-align: center !important; display: block !important; box-shadow: none !important;
    }
    .contenedor-rojo div[data-testid="stButton"] > button:hover { background-color: #9f1239 !important; }
    .contenedor-rojo div[data-testid="stButton"] > button p, .contenedor-rojo div[data-testid="stButton"] > button span { color: white !important; }
    
    /* 🟢 ENVOLTURA PARA FORZAR EL BOTÓN EN VERDE (Guardar) */
    .contenedor-verde div[data-testid="stButton"] > button {
        background-color: #10b981 !important; color: white !important; border: none !important;
        font-size: 18px !important; font-weight: 700 !important; text-align: center !important; 
        display: block !important; box-shadow: none !important; padding: 14px 20px !important;
    }
    .contenedor-verde div[data-testid="stButton"] > button:hover { background-color: #059669 !important; }
    .contenedor-verde div[data-testid="stButton"] > button p, .contenedor-verde div[data-testid="stButton"] > button span { color: white !important; }
    
    /* Botones pequeños de los historiales */
    div[data-testid="stButton"] > button[key*="edit_baja_"] {
        padding: 6px 12px !important; font-size: 12px !important; border-radius: 8px !important; width: auto !important;
    }
    
    /* Botón Volver superior */
    .back-button div[data-testid="stButton"] > button {
        background-color: #f1f5f9 !important; color: #475569 !important; padding: 8px 16px !important;
        font-size: 14px !important; border-radius: 10px !important; border: 1px solid #e2e8f0 !important; margin-bottom: 15px !important;
        width: auto !important; display: inline-block !important; text-align: center !important;
    }
    .back-button div[data-testid="stButton"] > button p, .back-button div[data-testid="stButton"] > button span { color: #475569 !important; }
</style>
""", unsafe_allow_html=True)

# Conexión Supabase
@st.cache_resource
def get_supabase_client():
    try:
        supabase_url = st.secrets.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY")
        if not supabase_url or not supabase_key: return None, "Faltan credenciales."
        return create_client(supabase_url, supabase_key), None
    except Exception as e: return None, str(e)

# Inicializar estados de la sesión
if "menu_actual" not in st.session_state: st.session_state.menu_actual = "INICIO"
if "sobreescribir_muertes" not in st.session_state: st.session_state.sobreescribir_muertes = False
if "sobreescribir_inventario" not in st.session_state: st.session_state.sobreescribir_inventario = False
if "temp_muertes" not in st.session_state: st.session_state.temp_muertes = None
if "temp_inventario" not in st.session_state: st.session_state.temp_inventario = None
if "mostrar_vista_rapida" not in st.session_state: st.session_state.mostrar_vista_rapida = False

if "valores_edit_bajas" not in st.session_state: st.session_state.valores_edit_bajas = {"G1": "", "G2": "", "G3": "", "G4": "", "obs": "", "fecha": None}
if "valores_edit_inv" not in st.session_state: st.session_state.valores_edit_inv = {}

tz_chile = pytz.timezone('America/Santiago')
fecha_hoy_default = datetime.now(tz_chile).date()

# =====================================================================
# PANTALLA 1: MENÚ PRINCIPAL
# =====================================================================
if st.session_state.menu_actual == "INICIO":
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="menu-header"><span style="font-weight:800; font-size:18px; color:#1e293b !important;">Avícola Santa Valentina</span><span class="badge-op">OP-1</span></div>', unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; font-size:42px; margin-bottom:10px; margin-top:10px;'>🚜</div>", unsafe_allow_html=True)
        st.markdown('<div class="header-title">¿Qué deseas registrar hoy?</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-subtitle">Selecciona uno de los módulos de abajo para ingresar el parte diario del campo.</div>', unsafe_allow_html=True)
        
        if st.button("📝 Registrar Bajas (Muertes) ➔", use_container_width=True, key="btn_bajas"):
            st.session_state.valores_edit_bajas = {"G1": "", "G2": "", "G3": "", "G4": "", "obs": "", "fecha": None}
            st.session_state.menu_actual = "BAJAS"
            st.rerun()
            
        if st.button("🥚 Inventario de Huevos ➔", use_container_width=True, key="btn_inventario"):
            st.session_state.valores_edit_inv = {}
            st.session_state.menu_actual = "INVENTARIO"
            st.rerun()
            
        # ENVOLTURA EN CONTENEDOR ROJO CON SELECTOR COMPLETO
        st.markdown('<div class="contenedor-rojo">', unsafe_allow_html=True)
        if st.button("📦 Ver Inventario General (Rápido) ➔", use_container_width=True, key="btn_ver_inv"):
            st.session_state.mostrar_vista_rapida = not st.session_state.mostrar_vista_rapida
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
        if st.session_state.mostrar_vista_rapida:
            st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 2px dashed #cbd5e1;'>", unsafe_allow_html=True)
            supabase_client, error_msg = get_supabase_client()
            if supabase_client and not error_msg:
                try:
                    res_ultimo = supabase_client.table("resumen_inventario_diario").select("*").limit(1).execute()
                    if res_ultimo.data:
                        datos_raw = res_ultimo.data[0]
                        fecha_registro_inv = datos_raw.pop("fecha")
                        
                        total_color = sum(int(v or 0) for k, v in datos_raw.items() if "Color" in k)
                        total_blanco = sum(int(v or 0) for k, v in datos_raw.items() if "Blanco" in k)
                        
                        st.markdown(f"<span style='font-weight:bold;'>📊 Consolidado General (Cierre: {fecha_registro_inv})</span>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="totales-container">
                            <div class="total-box" style="background-color: #fef3c7 !important; border-color: #fde68a !important;"><div class="lbl-box" style="color: #92400e !important;">Total Color</div><div class="val-box" style="color: #92400e !important;">{total_color}</div></div>
                            <div class="total-box" style="background-color: #f1f5f9 !important; border-color: #e2e8f0 !important;"><div class="lbl-box" style="color: #334155 !important;">Total Blanco</div><div class="val-box" style="color: #334155 !important;">{total_blanco}</div></div>
                            <div class="total-box" style="background-color: #ecfdf5 !important; border-color: #a7f3d0 !important;"><div class="lbl-box" style="color: #065f46 !important;">Total General</div><div class="val-box" style="color: #065f46 !important;">{total_color + total_blanco}</div></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("✏️ Corregir / Editar Inventario de Hoy", use_container_width=True, key="edit_inv_hoy"):
                            mapeo_llaves = {
                                "Color S. Jumbo": "color_super_jumbo", "Color Jumbo": "color_jumbo", "Color Super": "color_super", "Color Extra": "color_extra",
                                "Color 1ra": "color_primera", "Color 2da": "color_segunda", "Color 3ra": "color_tercera", "Color 4ta": "color_cuarta",
                                "Blanco S. Jumbo": "blanco_super_jumbo", "Blanco Jumbo": "blanco_jumbo", "Blanco Super": "blanco_super", "Blanco Extra": "blanco_extra",
                                "Blanco 1ra": "blanco_primera", "Blanco 2da": "blanco_segunda", "Blanco 3ra": "blanco_tercera", "Blanco 4ta": "blanco_cuarta"
                            }
                            inv_para_cargar = {}
                            for vista_name, tabla_key in mapeo_llaves.items():
                                inv_para_cargar[tabla_key] = str(datos_raw.get(vista_name, ""))
                            
                            st.session_state.valores_edit_inv = inv_para_cargar
                            st.session_state.menu_actual = "INVENTARIO"
                            st.rerun()

                        df_items = pd.DataFrame(list(datos_raw.items()), columns=["Tipo de Huevo", "Cantidad"])
                        df_filtrado = df_items[df_items["Cantidad"] > 0]
                        if not df_filtrado.empty:
                            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
                    else: st.info("📭 No se registran datos de inventario.")
                except Exception as e: st.error(str(e))
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# PANTALLA 2: FORMULARIO DE BAJAS
# =====================================================================
elif st.session_state.menu_actual == "BAJAS":
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="back-button">', unsafe_allow_html=True)
        if st.button("⬅ Volver al Menú Principal", key="back_m"):
            st.session_state.menu_actual = "INICIO"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="header-title">🐔 Registro de Bajas</div>', unsafe_allow_html=True)
        
        v_bajas = st.session_state.valores_edit_bajas
        if v_bajas["fecha"]:
            st.info(f"✏️ Modo Edición: Modificando registro del {v_bajas['fecha']}")
            fecha_str = v_bajas["fecha"]
        else:
            fecha_seleccionada = st.date_input("Fecha muertas", value=fecha_hoy_default, label_visibility="collapsed", key="fecha_m")
            fecha_str = fecha_seleccionada.strftime('%Y-%m-%d')
        
        entradas_crudas = {}
        col1, col2 = st.columns(2)
        with col1:
            entradas_crudas["Galpón 1"] = st.text_input("🏠 Galpón 1 (24 semanas)", value=v_bajas["G1"], placeholder="Ej: 0", key="g1_input")
            entradas_crudas["Galpón 2"] = st.text_input("🥚 Galpón 2 (42 semanas)", value=v_bajas["G2"], placeholder="Ej: 0", key="g2_input")
        with col2:
            entradas_crudas["Galpón 3"] = st.text_input("🌽 Galpón 3 (16 semanas)", value=v_bajas["G3"], placeholder="Ej: 0", key="g3_input")
            entradas_crudas["Galpón 4"] = st.text_input("🚜 Galpón 4 (56 semanas)", value=v_bajas["G4"], placeholder="Ej: 0", key="g4_input")
            
        observacion = st.text_area("Observaciones (Opcional) 📝", value=v_bajas["obs"], placeholder="Ej: Ventilador malo...", max_chars=200, key="obs_m")
        
        # ENVOLTURA EN CONTENEDOR VERDE CON SELECTOR DEL ELEMENTO REAL
        st.markdown('<div class="contenedor-verde">', unsafe_allow_html=True)
        guardar = st.button("💾 Guardar Registro de Bajas", use_container_width=True, key="btn_save_bajas")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        
        with st.expander("📊 Historial Semanal / Botones de Edición", expanded=False):
            supabase_client, error_msg = get_supabase_client()
            if supabase_client and not error_msg:
                try:
                    hace_una_semana = (datetime.now(tz_chile) - timedelta(days=7)).strftime('%Y-%m-%d')
                    res_h = supabase_client.table("resumen_bajas_diarias").select("*").gte("fecha", hace_una_semana).execute()
                    if res_h.data:
                        for row in res_h.data:
                            col_f1, col_f2 = st.columns([3, 1])
                            with col_f1:
                                st.markdown(f"**📅 {row['fecha']}** | G1: `{row['g1']}` | G2: `{row['g2']}` | G3: `{row['g3']}` | G4: `{row['g4']}`")
                            with col_f2:
                                if st.button("✏️", key=f"edit_baja_{row['fecha']}"):
                                    st.session_state.valores_edit_bajas = {
                                        "G1": str(row['g1']), "G2": str(row['g2']), "G3": str(row['g3']), "G4": str(row['g4']),
                                        "obs": row['observacion'] if row['observacion'] else "", "fecha": row['fecha']
                                    }
                                    st.rerun()
                    else: st.info("📅 Sin registros esta semana.")
                except Exception as e: st.error(str(e))

        if guardar:
            payload_data = {}
            valores_invalidos = False
            campos_vacios = False
            for k, v in entradas_crudas.items():
                v_clean = v.strip()
                if not v_clean: campos_vacios = True; break
                if not v_clean.isdigit(): valores_invalidos = True; break
                payload_data[k] = int(v_clean)
                
            if campos_vacios: st.error("⚠️ Rellena todos los campos.")
            elif valores_invalidos: st.error("⚠️ Solo números enteros.")
            else:
                supabase_client, _ = get_supabase_client()
                if v_bajas["fecha"]:
                    supabase_client.table("registro_bajas").delete().eq("fecha", fecha_str).execute()
                    payload = [{"galpon": int(g.replace("Galpón ", "")), "cantidad_muertas": q, "observacion": observacion.strip(), "fecha": fecha_str} for g, q in payload_data.items()]
                    supabase_client.table("registro_bajas").insert(payload).execute()
                    st.session_state.valores_edit_bajas = {"G1": "", "G2": "", "G3": "", "G4": "", "obs": "", "fecha": None}
                    st.success("🎉 Registro actualizado con éxito.")
                    st.rerun()
                else:
                    res = supabase_client.table("registro_bajas").select("fecha").eq("fecha", fecha_str).limit(1).execute()
                    if res.data:
                        st.session_state.temp_muertes = {"data": payload_data, "obs": observacion, "fecha": fecha_str}
                        st.session_state.sobreescribir_muertes = True
                        st.rerun()
                    else:
                        payload = [{"galpon": int(g.replace("Galpón ", "")), "cantidad_muertas": q, "observacion": observacion.strip(), "fecha": fecha_str} for g, q in payload_data.items()]
                        supabase_client.table("registro_bajas").insert(payload).execute()
                        st.success("🎉 ¡Guardado con éxito!")
                        st.balloons()

        if st.session_state.sobreescribir_muertes and st.session_state.temp_muertes:
            t_m = st.session_state.temp_muertes
            if t_m["fecha"] == fecha_str:
                st.warning("⚠️ Ya existe un registro para esta fecha. ¿Deseas sobrescribirlo?")
                if st.button("⚠️ Sí, sobrescribir datos", use_container_width=True):
                    supabase_client, _ = get_supabase_client()
                    supabase_client.table("registro_bajas").delete().eq("fecha", fecha_str).execute()
                    payload = [{"galpon": int(g.replace("Galpón ", "")), "cantidad_muertas": q, "observacion": t_m["obs"].strip(), "fecha": fecha_str} for g, q in t_m["data"].items()]
                    supabase_client.table("registro_bajas").insert(payload).execute()
                    st.session_state.sobreescribir_muertes = False
                    st.success("🎉 Actualizado con éxito.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# PANTALLA 3: FORMULARIO DE INVENTARIO
# =====================================================================
elif st.session_state.menu_actual == "INVENTARIO":
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="back-button">', unsafe_allow_html=True)
        if st.button("⬅ Volver al Menú Principal", key="back_i"):
            st.session_state.menu_actual = "INICIO"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="header-title">🥚 Inventario de Producción</div>', unsafe_allow_html=True)
        
        fecha_seleccionada = st.date_input("Fecha inventario", value=fecha_hoy_default, label_visibility="collapsed", key="fecha_i")
        fecha_str = fecha_seleccionada.strftime('%Y-%m-%d')
        
        lista_tamanos = ["Super Jumbo", "Jumbo", "Super", "Extra", "Primera", "Segunda", "Tercera", "Cuarta"]
        inventario_inputs = {}
        v_inv = st.session_state.valores_edit_inv
        
        st.markdown('<div class="section-banner-color">🟤 HUEVOS DE COLOR</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        for idx, tamano in enumerate(lista_tamanos):
            target_col = col_c1 if idx % 2 == 0 else col_c2
            key_name = f"color_{tamano.lower().replace(' ', '_')}"
            val_defecto = v_inv.get(key_name, "")
            with target_col:
                inventario_inputs[key_name] = st.text_input(f"Color {tamano}", value=val_defecto, placeholder="0 (Vacío)", key=f"c_{tamano}")
                
        st.markdown('<div class="section-banner-blanco">⚪ HUEVOS BLANCOS</div>', unsafe_allow_html=True)
        col_b1, col_b2 = st.columns(2)
        for idx, tamano in enumerate(lista_tamanos):
            target_col = col_b1 if idx % 2 == 0 else col_b2
            key_name = f"blanco_{tamano.lower().replace(' ', '_')}"
            val_defecto = v_inv.get(key_name, "")
            with target_col:
                inventario_inputs[key_name] = st.text_input(f"Blanco {tamano}", value=val_defecto, placeholder="0 (Vacío)", key=f"b_{tamano}")
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ENVOLTURA EN CONTENEDOR VERDE CON SELECTOR DEL ELEMENTO REAL
        st.markdown('<div class="contenedor-verde">', unsafe_allow_html=True)
        guardar_inv = st.button("💾 Guardar Inventario de Huevos", use_container_width=True, key="btn_save_inventario")
        st.markdown('</div>', unsafe_allow_html=True)

        if guardar_inv:
            valores_invalidos = False
            payload_inventario = {"fecha": fecha_str}
            for key, val_crudo in inventario_inputs.items():
                val_limpio = val_crudo.strip()
                if not val_limpio: payload_inventario[key] = 0
                else:
                    if not val_limpio.isdigit(): valores_invalidos = True; break
                    payload_inventario[key] = int(val_limpio)
            
            if valores_invalidos: st.error("⚠️ Solo números enteros positivos.")
            else:
                supabase_client, _ = get_supabase_client()
                try:
                    res_inv = supabase_client.table("registro_inventario").select("fecha").eq("fecha", fecha_str).limit(1).execute()
                    if res_inv.data:
                        st.session_state.temp_inventario = {"payload": payload_inventario, "fecha": fecha_str}
                        st.session_state.sobreescribir_inventario = True
                        st.rerun()
                    else:
                        supabase_client.table("registro_inventario").insert(payload_inventario).execute()
                        st.session_state.valores_edit_inv = {}
                        st.success("🎉 ¡Inventario registrado exitosamente!")
                        st.balloons()
                except Exception as e: st.error(str(e))

        if st.session_state.sobreescribir_inventario and st.session_state.temp_inventario:
            t_i = st.session_state.temp_inventario
            if t_i["fecha"] == fecha_str:
                st.warning(f"⚠️ Ya se envió un reporte de inventario para el {fecha_str}. ¿Deseas sobrescribirlo?")
                if st.button("⚠️ Sí, deseo sobrescribir el inventario", use_container_width=True):
                    supabase_client, _ = get_supabase_client()
                    try:
                        supabase_client.table("registro_inventario").delete().eq("fecha", fecha_str).execute()
                        supabase_client.table("registro_inventario").insert(t_i["payload"]).execute()
                        st.session_state.sobreescribir_inventario = False
                        st.session_state.valores_edit_inv = {}
                        st.success("🎉 ¡Inventario corregido con éxito!")
                        st.rerun()
                    except Exception as e: st.error(str(e))
        st.markdown('</div>', unsafe_allow_html=True)
