import streamlit as st
import assemblyai as aai
import tempfile
import os

# Configuración de la página
st.set_page_config(page_title="Multi-Transcriptor", page_icon="📹")
st.title("📹 Transcriptor de Múltiples Videos")
st.write("Sube uno o varios videoclips y la IA los transcribirá todos.")

# Configuración de la API (Asegúrate de tenerla en Secrets o ponerla aquí)
aai.settings.api_key = st.secrets["6322dc32094e44ee954749f961ac88b2"]

# CAMBIO CLAVE: Añadimos 'accept_multiple_files=True'
uploaded_files = st.file_uploader(
    "Selecciona tus videos", 
    type=["mp4", "mov", "avi", "mkv"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Has subido {len(uploaded_files)} videos. Haz clic abajo para empezar.")
    
    if st.button("Transcribir todo"):
        # Recorremos cada archivo subido
        for i, uploaded_file in enumerate(uploaded_files):
            # Usamos un 'expander' para que cada video tenga su propia sección colapsable
            with st.expander(f"Video {i+1}: {uploaded_file.name}", expanded=True):
                with st.spinner(f"Procesando '{uploaded_file.name}'..."):
                    
                    # 1. Crear archivo temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                        temp_video.write(uploaded_file.read())
                        temp_video_path = temp_video.name
                    
                    try:
                        # 2. Configurar y Transcribir (con el modelo corregido)
                        transcriber = aai.Transcriber()
                        config = aai.TranscriptionConfig(
                            speech_models=["universal-3-pro", "universal-2"],
                            language_code="es"
                        )
                        
                        transcript = transcriber.transcribe(temp_video_path, config=config)
                        
                        if transcript.status == aai.TranscriptStatus.error:
                            st.error(f"Error: {transcript.error}")
                        else:
                            st.success(f"¡Listo!")
                            # Mostramos el texto resultante
                            st.text_area("Transcripción:", transcript.text, height=200, key=f"text_{i}")
                    
                    except Exception as e:
                        st.error(f"Ocurrió un error inesperado: {e}")
                    finally:
                        # Limpiar temporal
                        os.remove(temp_video_path)

        st.balloons() # ¡Efecto visual al terminar todo!
