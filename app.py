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

# Estilos CSS avanzados para replicar EXACTAMENTE la interfaz de tus imágenes
st.markdown("""
<style>
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; height: 0px !important; padding: 0px !important; }
    footer { visibility: hidden; }

    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    div[data-testid="stVerticalBlock"] > div:first-child { margin-top: 0px !important; padding-top: 0px !important; }
    .stApp { background-color: #f8fafc; }
    
    /* Contenedor tipo tarjeta central */
    .main-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
        border: 1px solid #f1f5f9;
    }
    
    /* Encabezado e identificador OP-1 */
    .menu-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .badge-op {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    
    .header-title { color: #0f172a; font-size: 24px; font-weight: 700; text-align: center; margin-bottom: 4px; }
    .header-subtitle { color: #64748b; font-size: 14px; text-align: center; margin-bottom: 24px; }
    
    /* Banners estéticos de inventario */
    .section-banner-color {
        background-color: #fef3c7; color: #92400e; padding: 10px; border-radius: 10px;
        font-weight: bold; font-size: 16px; text-align: center; margin: 20px 0 10px 0; border: 1px solid #fde68a;
    }
    .section-banner-blanco {
        background-color: #f1f5f9; color: #334155; padding: 10px; border-radius: 10px;
        font-weight: bold; font-size: 16px; text-align: center; margin: 25px 0 10px 0; border: 1px solid #e2e8f0;
    }
    
    /* Tarjetas de Totales de Cajas */
    .totales-container {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
        margin-top: 10px;
    }
    .total-box {
        flex: 1;
        padding: 12px 8px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        border: 1px solid #e2e8f0;
    }
    .val-box { font-size: 18px; font-weight: 700; margin-top: 2px; }
    .lbl-box { font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; }
    
    div[data-baseweb="select"], div[data-baseweb="input"] { border-radius: 10px; }
    
    /* Botones nativos estilizados como Tarjetas de Menú */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        padding: 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        text-align: left !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        transition: all 0.2s ease-in-out !important;
        margin-bottom: 12px !important;
    }
    div.stButton > button:hover {
        border-color: #cbd5e1 !important;
        background-color: #f8fafc !important;
        transform: translateY(-2px) !important;
    }
    
    /* Estilo exclusivo para el botón de Ver Inventario Rápido */
    div.stButton > button[key*="btn_ver_inv"] {
        background-color: #be123c !important;
        color: white !important;
        border: none !important;
    }
    div.stButton > button[key*="btn_ver_inv"]:hover {
        background-color: #9f1239 !important;
    }
    
    /* Botones de Acción (Guardar, Volver, Sobrescribir) */
    .action-button button {
        background-color: #10b981 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3) !important;
        text-align: center !important;
    }
    .action-button button:hover { background-color: #059669 !important; color: white !important; }
    
    /* Estilo para botón volver superior */
    .back-button button {
        background-color: #f1f5f9 !important;
        color: #475569 !important;
        padding: 8px 16px !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        text-align: center !important;
        margin-bottom: 15px !important;
    }
    
    .override-button-container button {
        background-color: #f59e0b !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        border: none !important;
        text-align: center !important;
    }
    .override-button-container button:hover { background-color: #d97706 !important; color: white !important; }
    
    label { font-weight: 600 !important; color: #475569 !important; font-size: 14px !important; }
    
    .success-box {
        padding: 16px; border-radius: 12px; background-color: #ecfdf5;
        border: 1px solid #a7f3d0; color: #065f46; font-size: 15px;
        font-weight: 500; text-align: center; margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Conexión Supabase
@st.cache_resource
def get_supabase_client():
    try:
        supabase_url = st.secrets.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            return None, "Faltan credenciales."
        return create_client(supabase_url, supabase_key), None
    except Exception as e:
        return None, str(e)

# Inicializar estados de la sesión
if "menu_actual" not in st.session_state: st.session_state.menu_actual = "INICIO"
if "mostrar_error" not in st.session_state: st.session_state.mostrar_error = False
if "sobreescribir_muertes" not in st.session_state: st.session_state.sobreescribir_muertes = False
if "sobreescribir_inventario" not in st.session_state: st.session_state.sobreescribir_inventario = False
if "temp_muertes" not in st.session_state: st.session_state.temp_muertes = None
if "temp_inventario" not in st.session_state: st.session_state.temp_inventario = None
if "mostrar_vista_rapida" not in st.session_state: st.session_state.mostrar_vista_rapida = False

tz_chile = pytz.timezone('America/Santiago')
fecha_hoy_default = datetime.now(tz_chile).date()

# =====================================================================
# PANTALLA 1: MENÚ PRINCIPAL INTERACTIVO
# =====================================================================
if st.session_state.menu_actual == "INICIO":
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="menu-header"><span style="font-weight:800; font-size:18px; color:#1e293b;">Avícola Santa Valentina</span><span class="badge-op">OP-1</span></div>', unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; font-size:42px; margin-bottom:10px; margin-top:10px;'>🚜</div>", unsafe_allow_html=True)
        st.markdown('<div class="header-title">¿Qué deseas registrar hoy?</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-subtitle">Selecciona uno de los módulos de abajo para ingresar el parte diario del campo.</div>', unsafe_allow_html=True)
        
        if st.button("📝 Registrar Bajas (Muertes) ➔", use_container_width=True, key="btn_bajas"):
            st.session_state.menu_actual = "BAJAS"
            st.session_state.mostrar_vista_rapida = False
            st.rerun()
            
        if st.button("🥚 Inventario de Huevos ➔", use_container_width=True, key="btn_inventario"):
            st.session_state.menu_actual = "INVENTARIO"
            st.session_state.mostrar_vista_rapida = False
            st.rerun()
            
        if st.button("📦 Ver Inventario General (Rápido) ➔", use_container_width=True, key="btn_ver_inv"):
            st.session_state.mostrar_vista_rapida = not st.session_state.mostrar_vista_rapida
            st.rerun()
            
        # DESPLEGABLE CON CÁLCULO DE CAJAS (360 HUEVOS POR CAJA)
        if st.session_state.mostrar_vista_rapida:
            st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 2px dashed #cbd5e1;'>", unsafe_allow_html=True)
            supabase_client, error_msg = get_supabase_client()
            if supabase_client and not error_msg:
                try:
                    res_ultimo = supabase_client.table("resumen_inventario_diario").select("*").limit(1).execute()
                    if res_ultimo.data:
                        datos_raw = res_ultimo.data[0]
                        fecha_registro_inv = datos_raw.pop("fecha")
                        
                        # --- CÁLCULO LOGÍSTICO DE CAJAS ---
                        total_color = 0
                        total_blanco = 0
                        
                        for key, cantidad in datos_raw.items():
                            if "Color" in key:
                                total_color += int(cantidad or 0)
                            elif "Blanco" in key:
                                total_blanco += int(cantidad or 0)
                                
                        # Conversión a cajas (unidades / 360) redondeado a 1 decimal
                        cajas_color = round(total_color / 360, 1)
                        cajas_blanco = round(total_blanco / 360, 1)
                        cajas_total = round((total_color + total_blanco) / 360, 1)
                        
                        # --- DISEÑO DE TARJETAS DE RESUMEN DE CAJAS ---
                        st.markdown(f"**📊 Consolidado de Cajas (Cierre: {fecha_registro_inv})**")
                        st.markdown(f"""
                        <div class="totales-container">
                            <div class="total-box" style="background-color: #fef3c7; border-color: #fde68a;">
                                <div class="lbl-box" style="color: #92400e;">📦 Cajas Color</div>
                                <div class="val-box" style="color: #92400e;">{cajas_color}</div>
                            </div>
                            <div class="total-box" style="background-color: #f1f5f9; border-color: #e2e8f0;">
                                <div class="lbl-box" style="color: #334155;">📦 Cajas Blanco</div>
                                <div class="val-box" style="color: #334155;">{cajas_blanco}</div>
                            </div>
                            <div class="total-box" style="background-color: #ecfdf5; border-color: #a7f3d0;">
                                <div class="lbl-box" style="color: #065f46;">📊 Total General</div>
                                <div class="val-box" style="color: #065f46;">{cajas_total}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Mostrar el detalle vertical filtrando los ceros
                        df_items = pd.DataFrame(list(datos_raw.items()), columns=["Tipo de Huevo", "Cantidad"])
                        df_filtrado = df_items[df_items["Cantidad"] > 0]
                        
                        if not df_filtrado.empty:
                            st.markdown("<p style='font-size:13px; color:#64748b; font-weight:600; margin-bottom:5px;'>DETALLE DE UNIDADES EN STOCK:</p>", unsafe_allow_html=True)
                            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
                        else:
                            st.info(f"📋 El último inventario cargado no registra unidades individuales mayores a 0.")
                    else: st.info("📭 No se registran datos de inventario.")
                except Exception as e: st.error(str(e))
            else: st.error("Error de conexión.")
            
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# PANTALLA 2: FORMULARIO DE BAJAS
# =====================================================================
elif st.session_state.menu_actual == "BAJAS":
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="menu-header"><div></div><span class="badge-op">OP-1</span></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="back-button">', unsafe_allow_html=True)
        if st.button("⬅ Volver al Menú Principal", key="back_m"):
            st.session_state.menu_actual = "INICIO"
            st.session_state.sobreescribir_muertes = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="header-title">🐔 Registro de Bajas</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-subtitle">MÓDULO MORTALIDAD</div>', unsafe_allow_html=True)
        
        st.markdown("### 📅 Fecha de Registro")
        fecha_seleccionada = st.date_input("Fecha muertas", value=fecha_hoy_default, label_visibility="collapsed", key="fecha_m")
        fecha_str = fecha_seleccionada.strftime('%Y-%m-%d')
        
        st.markdown("### 📋 Cantidad de Bajas")
        entradas_crudas = {}
        col1, col2 = st.columns(2)
        with col1:
            entradas_crudas["Galpón 1"] = st.text_input("🏠 Galpón 1 (24 semanas)", value="", placeholder="Ej: 0")
            entradas_crudas["Galpón 2"] = st.text_input("🥚 Galpón 2 (42 semanas)", value="", placeholder="Ej: 0")
        with col2:
            entradas_crudas["Galpón 3"] = st.text_input("🌽 Galpón 3 (16 semanas)", value="", placeholder="Ej: 0")
            entradas_crudas["Galpón 4"] = st.text_input("🚜 Galpón 4 (56 semanas)", value="", placeholder="Ej: 0")
            
        st.markdown("<br>", unsafe_allow_html=True)
        observacion = st.text_area("Observaciones / Notas (Opcional) 📝", placeholder="Ej: Problemas de ventilación...", max_chars=200, key="obs_m")
        
        st.markdown('<div class="action-button">', unsafe_allow_html=True)
        guardar = st.button("💾 Guardar Registro de Bajas", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        with st.expander("📊 Ver Bajas de la Última Semana", expanded=False):
            supabase_client, error_msg = get_supabase_client()
            if supabase_client and not error_msg:
                try:
                    hace_una_semana = (datetime.now(tz_chile) - timedelta(days=7)).strftime('%Y-%m-%d')
                    response_historial = supabase_client.table("resumen_bajas_diarias").select("*").gte("fecha", hace_una_semana).execute()
                    if response_historial.data:
                        df_historial = pd.DataFrame(response_historial.data)
                        df_historial.columns = ["Fecha", "G1", "G2", "G3", "G4", "Notas"]
                        st.dataframe(df_historial, use_container_width=True, hide_index=True)
                    else: st.info("📅 No hay bajas registradas esta semana.")
                except Exception as e: st.error(str(e))

        if guardar:
            valores_invalidos = False
            campos_vacios = False
            payload_data = {}
            for k, v in entradas_crudas.items():
                v_clean = v.strip()
                if not v_clean: campos_vacios = True; break
                if not v_clean.isdigit(): valores_invalidos = True; break
                payload_data[k] = int(v_clean)
                
            if campos_vacios: st.error("⚠️ Debes rellenar los 4 galpones (escribe '0' si no hay bajas).")
            elif valores_invalidos: st.error("⚠️ Ingresa solo números enteros positivos.")
            else:
                supabase_client, error_msg = get_supabase_client()
                if supabase_client and not error_msg:
                    res = supabase_client.table("registro_bajas").select("fecha").eq("fecha", fecha_str).limit(1).execute()
                    if res.data:
                        st.session_state.temp_muertes = {"data": payload_data, "obs": observacion, "fecha": fecha_str}
                        st.session_state.sobreescribir_muertes = True
                        st.rerun()
                    else:
                        st.session_state.sobreescribir_muertes = False
                        with st.spinner("Guardando..."):
                            payload = [{"galpon": int(g.replace("Galpón ", "")), "cantidad_muertas": q, "observacion": observacion.strip(), "fecha": fecha_str} for g, q in payload_data.items()]
                            supabase_client.table("registro_bajas").insert(payload).execute()
                            st.success("🎉 ¡Bajas guardadas con éxito!")
                            st.balloons()

        if st.session_state.sobreescribir_muertes and st.session_state.temp_muertes:
            t_m = st.session_state.temp_muertes
            if t_m["fecha"] == fecha_str:
                st.warning(f"⚠️ Ya existe un registro de bajas para el {fecha_str}. ¿Deseas sobrescribirlo?")
                st.markdown('<div class="override-button-container">', unsafe_allow_html=True)
                confirmar_sobreescritura_m = st.button("⚠️ Sí, sobrescribir bajas del día", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if confirmar_sobreescritura_m:
                    supabase_client, _ = get_supabase_client()
                    supabase_client.table("registro_bajas").delete().eq("fecha", fecha_str).execute()
                    payload = [{"galpon": int(g.replace("Galpón ", "")), "cantidad_muertas": q, "observacion": t_m["obs"].strip(), "fecha": fecha_str} for g, q in t_m["data"].items()]
                    supabase_client.table("registro_bajas").insert(payload).execute()
                    st.session_state.sobreescribir_muertes = False
                    st.session_state.temp_muertes = None
                    st.success("🎉 ¡Bajas actualizadas con éxito!")
                    st.rerun()
            else: 
                st.session_state.sobreescribir_muertes = False
                st.session_state.temp_muertes = None

        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# PANTALLA 3: FORMULARIO DE INVENTARIO
# =====================================================================
elif st.session_state.menu_actual == "INVENTARIO":
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="menu-header"><div></div><span class="badge-op">OP-1</span></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="back-button">', unsafe_allow_html=True)
        if st.button("⬅ Volver al Menú Principal", key="back_i"):
            st.session_state.menu_actual = "INICIO"
            st.session_state.sobreescribir_inventario = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="header-title">🥚 Inventario de Producción</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-subtitle">Ingreso diario de huevos clasificados</div>', unsafe_allow_html=True)
        
        st.markdown("### 📅 Fecha de Inventario")
        fecha_seleccionada = st.date_input("Fecha inventario", value=fecha_hoy_default, label_visibility="collapsed", key="fecha_i")
        fecha_str = fecha_seleccionada.strftime('%Y-%m-%d')
        
        lista_tamanos = ["Super Jumbo", "Jumbo", "Super", "Extra", "Primera", "Segunda", "Tercera", "Cuarta"]
        inventario_inputs = {}
        
        # --- SECCIÓN 1: HUEVOS DE COLOR ---
        st.markdown('<div class="section-banner-color">🟤 HUEVOS DE COLOR</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        for idx, tamano in enumerate(lista_tamanos):
            target_col = col_c1 if idx % 2 == 0 else col_c2
            with target_col:
                inventario_inputs[f"color_{tamano.lower().replace(' ', '_')}"] = st.text_input(f"Color {tamano}", value="", placeholder="0 (Vacío)", key=f"c_{tamano}")
                
        # --- SECCIÓN 2: HUEVOS BLANCOS ---
        st.markdown('<div class="section-banner-blanco">⚪ HUEVOS BLANCOS</div>', unsafe_allow_html=True)
        col_b1, col_b2 = st.columns(2)
        for idx, tamano in enumerate(lista_tamanos):
            target_col = col_b1 if idx % 2 == 0 else col_b2
            with target_col:
                inventario_inputs[f"blanco_{tamano.lower().replace(' ', '_')}"] = st.text_input(f"Blanco {tamano}", value="", placeholder="0 (Vacío)", key=f"b_{tamano}")
                
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="action-button">', unsafe_allow_html=True)
        guardar_inv = st.button("💾 Guardar Inventario de Huevos", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        
        with st.expander("🔍 Ver Inventario Actual (Último Cargado)", expanded=False):
            supabase_client, error_msg = get_supabase_client()
            if supabase_client and not error_msg:
                try:
                    res_ultimo = supabase_client.table("resumen_inventario_diario").select("*").limit(1).execute()
                    if res_ultimo.data:
                        datos_raw = res_ultimo.data[0]
                        fecha_registro_inv = datos_raw.pop("fecha")
                        
                        df_items = pd.DataFrame(list(datos_raw.items()), columns=["Tipo de Huevo", "Cantidad"])
                        df_filtrado = df_items[df_items["Cantidad"] > 0]
                        
                        if not df_filtrado.empty:
                            st.markdown(f"**📦 Mostrando Cierre del Día: {fecha_registro_inv}**")
                            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
                        else:
                            st.info(f"📋 El último inventario cargado ({fecha_registro_inv}) se guardó completamente con valores en 0.")
                    else: st.info("📭 Aún no se han registrado inventarios.")
                except Exception as e: st.error(str(e))
            else: st.error("Error de conexión al servidor.")

        # Validación del inventario
        if guardar_inv:
            valores_invalidos = False
            payload_inventario = {"fecha": fecha_str}
            
            for key, val_crudo in inventario_inputs.items():
                val_limpio = val_crudo.strip()
                if not val_limpio:
                    payload_inventario[key] = 0
                else:
                    if not val_limpio.isdigit(): valores_invalidos = True; break
                    payload_inventario[key] = int(val_limpio)
            
            if valores_invalidos: st.error("⚠️ Solo se permiten números enteros positivos.")
            else:
                supabase_client, error_msg = get_supabase_client()
                if supabase_client and not error_msg:
                    try:
                        res_inv = supabase_client.table("registro_inventario").select("fecha").eq("fecha", fecha_str).limit(1).execute()
                        if res_inv.data:
                            st.session_state.temp_inventario = {"payload": payload_inventario, "fecha": fecha_str}
                            st.session_state.sobreescribir_inventario = True
                            st.rerun()
                        else:
                            st.session_state.sobreescribir_inventario = False
                            with st.spinner("Guardando inventario..."):
                                supabase_client.table("registro_inventario").insert(payload_inventario).execute()
                                st.success("🎉 ¡Inventario de huevos registrado exitosamente!")
                                st.balloons()
                    except Exception as e: st.error(str(e))

        if st.session_state.sobreescribir_inventario and st.session_state.temp_inventario:
            t_i = st.session_state.temp_inventario
            if t_i["fecha"] == fecha_str:
                st.warning(f"⚠️ Ya se envió un reporte de inventario hoy para la fecha {fecha_str}. ¿Deseas sobrescribirlo?")
                st.markdown('<div class="override-button-container">', unsafe_allow_html=True)
                ejecutar_sobreescritura_inv = st.button("⚠️ Sí, deseo sobrescribir el inventario", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if ejecutar_sobreescritura_inv:
                    supabase_client, _ = get_supabase_client()
                    try:
                        supabase_client.table("registro_inventario").delete().eq("fecha", fecha_str).execute()
                        supabase_client.table("registro_inventario").insert(t_i["payload"]).execute()
                        st.session_state.sobreescribir_inventario = False
                        st.session_state.temp_inventario = None
                        st.success("🎉 ¡Inventario sobrescrito con éxito!")
                        st.rerun()
                    except Exception as e: st.error(str(e))
            else: 
                st.session_state.sobreescribir_inventario = False
                st.session_state.temp_inventario = None

        st.markdown('</div>', unsafe_allow_html=True)
