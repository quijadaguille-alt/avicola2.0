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
    
    # Entradas verticales para cada uno de los 4 galpones (0 al infinito positivo)
    cantidades = {}
    
    col1, col2 = st.columns(2)
    with col1:
        cantidades["Galpón 1"] = st.number_input("🏠 Galpón 1 (24 semanas de vida)", min_value=0, value=None, step=1)
        cantidades["Galpón 2"] = st.number_input("🥚 Galpón 2 (42 semanas de vida)", min_value=0, value=None, step=1)
        
    with col2:
        cantidades["Galpón 3"] = st.number_input("🌽 Galpón 3 (16 semanas de vida)", min_value=0, value=None, step=1)
        cantidades["Galpón 4"] = st.number_input("🚜 Galpón 4 (56 semanas de vida)", min_value=0, value=None, step=1)
        
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
        # Validar si se ingresaron números decimales de forma manual o valores incorrectos
        valores_invalidos = False
        bajas_activas = {}
        
        for galpon_name, qty in cantidades.items():
            if qty is not None:
                # Si el número es menor a 0, o tiene decimales (no es igual a su parte entera)
                if qty < 0 or qty != int(qty):
                    valores_invalidos = True
                elif qty > 0:
                    bajas_activas[galpon_name] = int(qty)
        
        if valores_invalidos:
            st.session_state.mostrar_error = True
        elif not bajas_activas:
            st.error("⚠️ Debes ingresar al menos una baja (cantidad mayor a 0) en algún galpón para poder guardar.")
        else:
            st.session_state.mostrar_error = False # Limpiar error si todo es correcto
            supabase_client, error_msg = get_supabase_client()
            
            if error_msg:
                st.error(f"❌ Error de configuración: {error_msg}")
                st.info("💡 Por favor, asegúrate de configurar 'SUPABASE_URL' y 'SUPABASE_KEY' en la pestaña de Secretos (Secrets) de Streamlit.")
            elif not supabase_client:
                st.error("❌ No se pudo conectar a la base de datos Supabase.")
            else:
                # Intentar guardar los datos en Supabase
                with st.spinner("Enviando datos al servidor..."):
                    try:
                        payload = []
                        for galpon_name, qty in bajas_activas.items():
                            numero_galpon = int(galpon_name.replace("Galpón ", ""))
                            payload.append({
                                "galpon": numero_galpon,
                                "cantidad_muertas": int(qty),
                                "observacion": observacion.strip() if observacion else ""
                            })
                        
                        response = supabase_client.table("registro_bajas").insert(payload).execute()
                        
                        # Alerta visual de éxito
                        st.markdown(f"""
                            <div class="success-box">
                                🎉 ¡Registros Guardados con Éxito!<br>
                                <span style="font-size: 13px; font-weight: normal;">Se registraron las bajas de {len(bajas_activas)} galpón(es) correctamente en Supabase.</span>
                            </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Error al insertar datos en la base de datos: {str(e)}")
                        st.info("Verifica que la tabla 'registro_bajas' exista en Supabase con las columnas: galpon (text), cantidad_muertas (integer) y observacion (text).")

    # Muestra el aviso de error con el botón rojo para corregir el dato
    if st.session_state.mostrar_error:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("⚠️ ¡Valor Incorrecto detectado! Recuerda ingresar únicamente números enteros positivos (sin decimales ni signos negativos).")
        
        # Botón rojo estilizado usando el contenedor CSS
        st.markdown('<div class="error-button-container">', unsafe_allow_html=True)
        if st.button("🚨 Cambiar número", use_container_width=True):
            st.session_state.mostrar_error = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
                        
    st.markdown('</div>', unsafe_allow_html=True)
