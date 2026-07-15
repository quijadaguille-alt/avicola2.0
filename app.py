import streamlit as st
import os
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

# Control de estado de la pestaña de error de validación
if "mostrar_error" not in st.session_state:
    st.session_state.mostrar_error = False

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
    
    # 3. Observaciones opcionales
    observacion = st.text_area(
        "Observaciones / Notas (Opcional) 📝",
        placeholder="Ej: Problemas de ventilación, golpe de calor, goteo de bebederos...",
        max_chars=200
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. Botón de Guardar Registro
    guardar = st.button("💾 Guardar Registro", use_container_width=True)
    
    if guardar:
        valores_invalidos = False
        campos_vacios = False
        payload_data = {}
        
        # Primero revisamos si hay campos vacíos
        for galpon_name, valor_crudo in entradas_crudas.items():
            valor_limpio = valor_crudo.strip()
            
            # SI ALGÚN CAMPO ESTÁ VACÍO, SE MARCA COMO ERROR
            if not valor_limpio:
                campos_vacios = True
                break
                
            # Validar de forma súper estricta que solo contenga dígitos numéricos (del 0 al 9)
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
        
        if campos_vacios:
            st.error("⚠️ ¡Atención! Debes llenar los 4 cuadros (si no hay bajas en un galpón, escribe '0').")
        elif valores_invalidos:
            st.session_state.mostrar_error = True
        else:
            st.session_state.mostrar_error = False  # Limpiar error si todo es correcto
            supabase_client, error_msg = get_supabase_client()
            
            if error_msg:
                st.error(f"❌ Error de configuración: {error_msg}")
            elif not supabase_client:
                st.error("❌ No se pudo conectar a la base de datos Supabase.")
            else:
                # Intentar guardar los datos en Supabase
                with st.spinner("Enviando datos al servidor..."):
                    try:
                        payload = []
                        # Ahora procesamos TODOS los galpones (incluso los que se registraron con 0)
                        for galpon_name, qty in payload_data.items():
                            numero_galpon = int(galpon_name.replace("Galpón ", ""))
                            payload.append({
                                "galpon": numero_galpon,
                                "cantidad_muertas": qty,
                                "observacion": observacion.strip() if observacion else ""
                            })
                        
                        response = supabase_client.table("registro_bajas").insert(payload).execute()
                        
                        # Alerta visual de éxito
                        st.markdown(f"""
                            <div class="success-box">
                                🎉 ¡Registros Guardados con Éxito!<br>
                                <span style="font-size: 13px; font-weight: normal;">Se registraron los datos de los 4 galpones correctamente en Supabase.</span>
                            </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Error al insertar datos en la base de datos: {str(e)}")

    # Muestra el aviso de error con el botón rojo para corregir el dato
    if st.session_state.mostrar_error:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("⚠️ ¡Valor Incorrecto detectado! Recuerda ingresar únicamente números enteros positivos (sin letras, decimales, comas ni signos negativos).")
        
        # Botón rojo estilizado usando el contenedor CSS
        st.markdown('<div class="error-button-container">', unsafe_allow_html=True)
        if st.button("🚨 Cambiar número", use_container_width=True):
            st.session_state.mostrar_error = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
                        
    st.markdown('</div>', unsafe_allow_html=True)
