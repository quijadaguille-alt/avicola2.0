import streamlit as st
import os
from datetime import datetime
import pytz
from supabase import create_client, Client

# Configuración de la página optimizada para dispositivos móviles
st.set_page_config(
    page_title="Registro de Bajas",
    page_icon="🐔",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para UI limpia, responsiva y ocultar herramientas de desarrollo
st.markdown("""
<style>
    /* Ocultar el menú de tres puntos (opciones de desarrollo) */
    #MainMenu {
        visibility: hidden;
    }
    
    /* Ocultar la barra de estado superior de Streamlit */
    header {
        visibility: hidden;
    }
    
    /* Ocultar el pie de página de Streamlit */
    footer {
        visibility: hidden;
    }
     
    /* Estilo del fondo de la aplicación */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Contenedor tipo tarjeta central */
    .main-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
        border: 1px solid #f1f5f9;
    }
    
    /* Encabezado elegante */
    .header-title {
        color: #0f172a;
        font-size: 24px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 4px;
    }
    .header-subtitle {
        color: #64748b;
        font-size: 14px;
        text-align: center;
        margin-bottom: 24px;
    }
    
    /* Estilos para selectores y áreas de texto */
    div[data-baseweb="select"] {
        border-radius: 10px;
    }
    
    /* Botón Guardar (Verde) */
    .stButton>button {
        background-color: #10b981 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover {
        background-color: #059669 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 12px rgba(16, 185, 129, 0.4) !important;
    }
    .stButton>button:active {
        background-color: #047857 !important;
        transform: translateY(1px) !important;
    }
    
    /* Botón Sobrescribir (Amarillo / Naranja) */
    .override-button-container button {
        background-color: #f59e0b !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .override-button-container button:hover {
        background-color: #d97706 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 12px rgba(245, 158, 11, 0.4) !important;
    }

    /* Contenedor y diseño específico para el Botón Rojo de Error */
    .error-button-container button {
        background-color: #ef4444 !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .error-button-container button:hover {
        background-color: #dc2626 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 12px rgba(239, 68, 68, 0.4) !important;
    }
    
    /* Estilos para las etiquetas */
    label {
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 15px !important;
        margin-bottom: 6px !important;
    }
    
    /* Estilo para las alertas de éxito */
    .success-box {
        padding: 16px;
        border-radius: 12px;
        background-color: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        font-size: 15px;
        font-weight: 500;
        text-align: center;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar conexión a Supabase de forma segura
@st.cache_resource
def get_supabase_client():
    try:
        supabase_url = st.secrets.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            return None, "Faltan las credenciales de Supabase en Secrets."
            
        client = create_client(supabase_url, supabase_key)
        return client, None
    except Exception as e:
        return None, str(e)

# Control de estado interno de la app
if "mostrar_error" not in st.session_state:
    st.session_state.mostrar_error = False
if "sobreescribir_pendiente" not in st.session_state:
    st.session_state.sobreescribir_pendiente = False

# Obtener fecha actual en zona horaria de Chile para la verificación
tz_chile = pytz.timezone('America/Santiago')
fecha_hoy = datetime.now(tz_chile).strftime('%Y-%m-%d')

# Renderizado de la UI en la tarjeta principal
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown('<div class="header-title">🐔 Avícola Santa Valentina</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Registro rápido de bajas por galpón</div>', unsafe_allow_html=True)
    
    st.markdown("### 📋 Cantidad de Bajas por Galpón")
    
    entradas_crudas = {}
    
    col1, col2 = st.columns(2)
    with col1:
        entradas_crudas["Galpón 1"] = st.text_input("🏠 Galpón 1 (24 semanas de vida)", value="", placeholder="Ingresa cantidad (ej: 0)")
        entradas_crudas["Galpón 2"] = st.text_input("🥚 Galpón 2 (42 semanas de vida)", value="", placeholder="Ingresa cantidad (ej: 0)")
        
    with col2:
        entradas_crudas["Galpón 3"] = st.text_input("🌽 Galpón 3 (16 semanas de vida)", value="", placeholder="Ingresa cantidad (ej: 0)")
        entradas_crudas["Galpón 4"] = st.text_input("🚜 Galpón 4 (56 semanas de vida)", value="", placeholder="Ingresa cantidad (ej: 0)")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Observaciones opcionales
    observacion = st.text_area(
        "Observaciones / Notas (Opcional) 📝",
        placeholder="Ej: Problemas de ventilación, golpe de calor, goteo de bebederos...",
        max_chars=200
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Intentamos conectar a Supabase para verificar registros previos de hoy
    supabase_client, error_msg = get_supabase_client()
    registro_previo = None
    
    if supabase_client and not error_msg:
        try:
            # Consultamos si hoy ya tiene registros
            response_check = supabase_client.table("registro_bajas").select("fecha, hora").eq("fecha", fecha_hoy).limit(1).execute()
            if response_check.data:
                registro_previo = response_check.data[0]
        except Exception:
            pass

    # Función que limpia y valida los datos antes de operar
    def validar_entradas():
        valores_invalidos = False
        campos_vacios = False
        payload_data = {}
        
        for galpon_name, valor_crudo in entradas_crudas.items():
            valor_limpio = valor_crudo.strip()
            if not valor_limpio:
                campos_vacios = True
                break
            if not valor_limpio.isdigit():
                valores_invalidos = True
                break
            try:
                qty = int(valor_limpio)
                if qty < 0:
                    valores_invalidos = True
                    break
                else:
                    payload_data[galpon_name] = qty
            except ValueError:
                valores_invalidos = True
                break
                
        return campos_vacios, valores_invalidos, payload_data

    # SI YA EXISTE UN REGISTRO DE HOY
    if registro_previo and not st.session_state.sobreescribir_pendiente:
        # Formatear la hora bonita
        hora_cruda = datetime.strptime(registro_previo['hora'], "%H:%M:%S.%f" if "." in registro_previo['hora'] else "%H:%M:%S")
        hora_formateada = hora_cruda.strftime("%H:%M")
        
        # Mapeo de días en español
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_nombre = dias_semana[datetime.strptime(registro_previo['fecha'], '%Y-%m-%d').weekday()]
        
        st.warning(f"⚠️ ¡Atención! Ya se envió un registro hoy **{dia_nombre} {datetime.strptime(registro_previo['fecha'], '%Y-%m-%d').strftime('%d/%m')}** a las **{hora_formateada} hrs**.")
        st.info("Si continúas, los datos anteriores de hoy serán borrados por completo y se guardarán los nuevos.")
        
        # Botón para activar el flujo de sobrescritura
        st.markdown('<div class="override-button-container">', unsafe_allow_html=True)
        confirmar_intento = st.button("⚠️ Sí, deseo sobrescribir los datos de hoy", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if confirmar_intento:
            campos_vacios, valores_invalidos, payload_data = validar_entradas()
            if campos_vacios:
                st.error("⚠️ ¡Atención! Debes llenar los 4 cuadros primero (si no hay bajas en un galpón, escribe '0').")
            elif valores_invalidos:
                st.session_state.mostrar_error = True
            else:
                st.session_state.sobreescribir_pendiente = True
                st.rerun()

    else:
        # Botón de Guardar normal
        guardar = st.button("💾 Guardar Registro", use_container_width=True)
        
        # Si confirmamos la sobrescritura o se presiona guardar normal
        if guardar or st.session_state.sobreescribir_pendiente:
            campos_vacios, valores_invalidos, payload_data = validar_entradas()
            
            if campos_vacios:
                st.error("⚠️ ¡Atención! Debes llenar los 4 cuadros (si no hay bajas en un galpón, escribe '0').")
                st.session_state.sobreescribir_pendiente = False
            elif valores_invalidos:
                st.session_state.mostrar_error = True
                st.session_state.sobreescribir_pendiente = False
            else:
                st.session_state.mostrar_error = False
                
                if error_msg:
                    st.error(f"❌ Error de configuración: {error_msg}")
                elif not supabase_client:
                    st.error("❌ No se pudo conectar a la base de datos Supabase.")
                else:
                    with st.spinner("Procesando datos en el servidor..."):
                        try:
                            # 1. Si era una sobrescritura, BORRAMOS primero los registros viejos de hoy
                            if st.session_state.sobreescribir_pendiente or registro_previo:
                                supabase_client.table("registro_bajas").delete().eq("fecha", fecha_hoy).execute()
                            
                            # 2. Insertamos el nuevo payload
                            payload = []
                            for galpon_name, qty in payload_data.items():
                                numero_galpon = int(galpon_name.replace("Galpón ", ""))
                                payload.append({
                                    "galpon": numero_galpon,
                                    "cantidad_muertas": qty,
                                    "observacion": observacion.strip() if observacion else ""
                                })
                            
                            supabase_client.table("registro_bajas").insert(payload).execute()
                            
                            # Resetear estado de sobrescritura
                            st.session_state.sobreescribir_pendiente = False
                            
                            st.markdown(f"""
                                <div class="success-box">
                                    🎉 ¡Datos Guardados y Actualizados con Éxito!<br>
                                    <span style="font-size: 13px; font-weight: normal;">Los registros anteriores de hoy fueron actualizados correctamente en Supabase.</span>
                                </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error al procesar los datos: {str(e)}")
                            st.session_state.sobreescribir_pendiente = False

    # Muestra el aviso de error con el botón rojo para corregir el dato
    if st.session_state.mostrar_error:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("⚠️ ¡Valor Incorrecto detectado! Recuerda ingresar únicamente números enteros positivos (sin letras, decimales, comas ni signos negativos).")
        
        st.markdown('<div class="error-button-container">', unsafe_allow_html=True)
        if st.button("🚨 Cambiar número", use_container_width=True):
            st.session_state.mostrar_error = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
                        
    st.markdown('</div>', unsafe_allow_html=True)
