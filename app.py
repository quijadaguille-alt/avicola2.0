import streamlit as st
import os
from datetime import datetime, date
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
    
    /* Estilos para selectores, áreas de texto e inputs de fecha */
    div[data-baseweb="select"], div[data-baseweb="input"] {
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

# Inicializar variables de estado de forma segura
if "mostrar_error" not in st.session_state:
    st.session_state.mostrar_error = False
if "confirmacion_sobreescribir" not in st.session_state:
    st.session_state.confirmacion_sobreescribir = False
if "datos_temporales" not in st.session_state:
    st.session_state.datos_temporales = None
if "registro_previo" not in st.session_state:
    st.session_state.registro_previo = None

# Obtener fecha actual en zona horaria de Chile por defecto
tz_chile = pytz.timezone('America/Santiago')
fecha_hoy_default = datetime.now(tz_chile).date()

# Renderizado de la UI en la tarjeta principal
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown('<div class="header-title">🐔 Avícola Santa Valentina</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Registro rápido de bajas por galpón</div>', unsafe_allow_html=True)
    
    st.markdown("### 📅 Fecha de Registro")
    # Nuevo Selector de Fecha (viene por defecto con la fecha de hoy de Chile)
    fecha_seleccionada = st.date_input("Selecciona el día de las bajas", value=fecha_hoy_default)
    fecha_str = fecha_seleccionada.strftime('%Y-%m-%d')
    
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
    
    # 1. BOTÓN PRINCIPAL: GUARDAR REGISTRO
    guardar = st.button("💾 Guardar Registro", use_container_width=True)
    
    # Función que limpia y valida los datos
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

    # Al presionar el botón de Guardar
    if guardar:
        campos_vacios, valores_invalidos, payload_data = validar_entradas()
        
        if campos_vacios:
            st.error("⚠️ ¡Atención! Debes llenar los 4 cuadros (si no hay bajas en un galpón, escribe '0').")
            st.session_state.confirmacion_sobreescribir = False
        elif valores_invalidos:
            st.session_state.mostrar_error = True
            st.session_state.confirmacion_sobreescribir = False
        else:
            st.session_state.mostrar_error = False
            
            # Consultar en Supabase si ya hay datos de la fecha seleccionada
            supabase_client, error_msg = get_supabase_client()
            if supabase_client and not error_msg:
                try:
                    # Usamos la fecha_str que viene del st.date_input
                    response_check = supabase_client.table("registro_bajas").select("fecha, hora").eq("fecha", fecha_str).limit(1).execute()
                    
                    if response_check.data:
                        # ¡Ya existe registro para esta fecha seleccionada! Guardamos datos temporalmente en memoria
                        st.session_state.registro_previo = response_check.data[0]
                        st.session_state.datos_temporales = {
                            "payload_data": payload_data,
                            "observacion": observacion,
                            "fecha": fecha_str
                        }
                        st.session_state.confirmacion_sobreescribir = True
                    else:
                        # No hay registros en esta fecha: Guardar directamente
                        st.session_state.confirmacion_sobreescribir = False
                        with st.spinner("Enviando datos al servidor..."):
                            payload = []
                            for galpon_name, qty in payload_data.items():
                                numero_galpon = int(galpon_name.replace("Galpón ", ""))
                                payload.append({
                                    "galpon": numero_galpon,
                                    "cantidad_muertas": qty,
                                    "observacion": observacion.strip() if observacion else "",
                                    "fecha": fecha_str  # Guardar la fecha del selector
                                })
                            
                            supabase_client.table("registro_bajas").insert(payload).execute()
                            st.markdown("""
                                <div class="success-box">
                                    🎉 ¡Registros Guardados con Éxito!<br>
                                    <span style="font-size: 13px; font-weight: normal;">Se registraron las bajas correctamente en Supabase.</span>
                                </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                except Exception as e:
                    st.error(f"❌ Error al consultar la base de datos: {str(e)}")

    # 2. BLOQUE DE ADVERTENCIA DE SOBRESCRITURA (Aparece dinámicamente si ya hay datos de esa fecha)
    if st.session_state.confirmacion_sobreescribir and st.session_state.registro_previo:
        registro = st.session_state.registro_previo
        temp_data = st.session_state.datos_temporales
        
        # Asegurarse de que la advertencia corresponda a la fecha seleccionada actualmente
        if temp_data and temp_data["fecha"] == fecha_str:
            # Formatear la hora de forma amigable
            hora_cruda = datetime.strptime(registro['hora'], "%H:%M:%S.%f" if "." in registro['hora'] else "%H:%M:%S")
            hora_formateada = hora_cruda.strftime("%H:%M")
            
            # Mapeo del día en español
            dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            dia_nombre = dias_semana[datetime.strptime(registro['fecha'], '%Y-%m-%d').weekday()]
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.warning(f"⚠️ ¡Atención! Ya se envió un registro para la fecha **{dia_nombre} {datetime.strptime(registro['fecha'], '%Y-%m-%d').strftime('%d/%m')}** (guardado originalmente a las **{hora_formateada} hrs**).")
            st.info("Si continúas, los datos de ese día serán borrados por completo y se guardarán los nuevos números.")
            
            # Botón amarillo para ejecutar la sobrescritura
            st.markdown('<div class="override-button-container">', unsafe_allow_html=True)
            ejecutar_sobreescritura = st.button("⚠️ Sí, deseo sobrescribir los datos de hoy", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if ejecutar_sobreescritura:
                supabase_client, error_msg = get_supabase_client()
                
                if supabase_client and temp_data:
                    with st.spinner("Actualizando datos en el servidor..."):
                        try:
                            # 1. Borrar registros de la fecha seleccionada
                            supabase_client.table("registro_bajas").delete().eq("fecha", fecha_str).execute()
                            
                            # 2. Insertar los nuevos registros
                            payload = []
                            for galpon_name, qty in temp_data["payload_data"].items():
                                numero_galpon = int(galpon_name.replace("Galpón ", ""))
                                payload.append({
                                    "galpon": numero_galpon,
                                    "cantidad_muertas": qty,
                                    "observacion": temp_data["observacion"].strip() if temp_data["observacion"] else "",
                                    "fecha": fecha_str  # Insertar la fecha correcta del selector
                                })
                            
                            supabase_client.table("registro_bajas").insert(payload).execute()
                            
                            # Limpiar variables de estado
                            st.session_state.confirmacion_sobreescribir = False
                            st.session_state.datos_temporales = None
                            st.session_state.registro_previo = None
                            
                            st.markdown("""
                                <div class="success-box">
                                    🎉 ¡Datos Guardados y Actualizados con Éxito!<br>
                                    <span style="font-size: 13px; font-weight: normal;">Los registros anteriores de esa fecha fueron actualizados correctamente en Supabase.</span>
                                </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al sobrescribir los datos: {str(e)}")
        else:
            # Si el usuario cambió la fecha seleccionada en el date_input, limpiamos la confirmación previa
            st.session_state.confirmacion_sobreescribir = False

    # 3. MUESTRA EL AVISO DE ERROR SI SE DETECTAN LETRAS, NEGATIVOS O DECIMALES
    if st.session_state.mostrar_error:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("⚠️ ¡Valor Incorrecto detectado! Recuerda ingresar únicamente números enteros positivos (sin letras, decimales, comas ni signos negativos).")
        
        st.markdown('<div class="error-button-container">', unsafe_allow_html=True)
        if st.button("🚨 Cambiar número", use_container_width=True):
            st.session_state.mostrar_error = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
                        
    st.markdown('</div>', unsafe_allow_html=True)
