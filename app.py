import os
import base64
import streamlit as st
from openai import OpenAI

# ---------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Análisis de imagen de Yos 🏞️❤️",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Estilos CSS Personalizados
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Estilo del contenedor principal */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Encabezado principal */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    
    /* Botones personalizados */
    .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------
def encode_image(image_file):
    """Convierte la imagen cargada a base64."""
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# ---------------------------------------------------------
# Barra Lateral (Sidebar): Configuración y Parámetros
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Entrada segura de la API Key
    api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Tu clave se usará de forma segura durante la sesión."
    )
    
    # Intentar obtener la clave desde secretos o desde el input manual
    api_key = api_key_input or st.secrets.get("OPENAI_API_KEY", "")
    
    st.divider()
    st.header("🎛️ Parámetros del Modelo")
    
    # Selección de modelo y parámetros creativos
    model_choice = st.selectbox("Modelo", ["gpt-4o", "gpt-4o-mini"], index=0)
    temperature = st.slider("Creatividad (Temperature)", 0.0, 1.0, 0.4, 0.1)
    max_tokens = st.slider("Longitud máxima (Tokens)", 300, 2000, 1000, 100)

# ---------------------------------------------------------
# Encabezado Principal
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">Análisis de imagen de Yos 🏞️❤️</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Sube una imagen y deja que la IA analice su composición, elementos, texto o genere ideas visuales al instante.</p>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Disposición principal en 2 Columnas (Carga vs Resultado)
# ---------------------------------------------------------
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📸 Imagen de entrada")
    uploaded_file = st.file_uploader("Selecciona o arrastra una imagen", type=["jpg", "png", "jpeg", "webp"])
    
    if uploaded_file:
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
        
        # Opciones de análisis
        st.markdown("---")
        analysis_type = st.selectbox(
            "Enfoque del análisis",
            [
                "📝 Descripción completa",
                "🎨 Análisis de diseño y composición",
                "🔍 Extracción de texto (OCR)",
                "💡 Ideas de contenido y Alt Text"
            ]
        )
        
        # Pregunta o contexto adicional opcional
        custom_prompt = st.text_area(
            "Pregunta o contexto específico (opcional):",
            placeholder="Ejemplo: ¿Qué colores predominan? o ¿Qué transmite esta imagen?"
        )
        
        analyze_button = st.button("✨ Analizar imagen", type="primary")

with col_right:
    st.subheader("🤖 Resultado del Análisis")
    
    if uploaded_file and analyze_button:
        if not api_key:
            st.error("🔑 Por favor ingresa tu OpenAI API Key en la barra lateral para continuar.")
        else:
            client = OpenAI(api_key=api_key)
            base64_img = encode_image(uploaded_file)
            
            # Construcción del Prompt según el enfoque elegido
            prompts = {
                "📝 Descripción completa": "Realiza una descripción detallada y completa en español de todo lo que se observa en la imagen.",
                "🎨 Análisis de diseño y composición": "Analiza la imagen desde una perspectiva de diseño gráfico e interactivo: habla sobre la paleta de colores, la composición, la jerarquía visual, la tipografía (si aplica) y la intención estética en español.",
                "🔍 Extracción de texto (OCR)": "Extrae e identifica de forma limpia todo el texto visible en la imagen. Si hay código o listas, organízalos con formato Markdown en español.",
                "💡 Ideas de contenido y Alt Text": "Proporciona: 1. Un texto alternativo (Alt Text) accesible para la imagen. 2. Tres ideas creativas de cómo usar esta imagen en redes o proyectos. Responde en español."
            }
            
            prompt_system = prompts.get(analysis_type, "Describe la imagen en español.")
            if custom_prompt.strip():
                prompt_system += f"\n\nInstrucción adicional del usuario: {custom_prompt.strip()}"
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_system},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]
                }
            ]
            
            try:
                with st.spinner("Procesando imagen con IA..."):
                    response_placeholder = st.empty()
                    full_response = ""
                    
                    # Generación en streaming
                    stream = client.chat.completions.create(
                        model=model_choice,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=True
                    )
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            response_placeholder.markdown(full_response + "▌")
                    
                    response_placeholder.markdown(full_response)
                    
                    # Botón para descargar el análisis generado
                    st.download_button(
                        label="📥 Descargar Análisis (.txt)",
                        data=full_response,
                        file_name=f"analisis_{uploaded_file.name}.txt",
                        mime="text/plain"
                    )
                    
            except Exception as e:
                st.error(f"Error al procesar la solicitud: {e}")
    elif not uploaded_file:
        st.info("👈 Sube una imagen en el panel izquierdo para comenzar el análisis.")
