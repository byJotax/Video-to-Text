import streamlit as st
import assemblyai as aai
import tempfile
import os

# 1. Configuración de la página
st.set_page_config(page_title="Transcriptor Pro", page_icon="📹")
st.title("📹 Transcriptor de Videos")

# 2. Configuración de la API (Usa el nombre de la etiqueta, no el valor directo)
try:
    aai.settings.api_key = st.secrets["ASSEMBLYAI_API_KEY"]
except:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")

# 3. Subida de archivos
uploaded_files = st.file_uploader(
    "Selecciona uno o varios videos", 
    type=["mp4", "mov", "avi", "mkv"], 
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Empezar Transcripción"):
        for i, file in enumerate(uploaded_files):
            with st.expander(f"Resultado: {file.name}", expanded=True):
                with st.spinner("Procesando..."):
                    # Crear temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        tmp.write(file.read())
                        path = tmp.name
                    
                    try:
                        transcriber = aai.Transcriber()
                        # Configuración obligatoria actualizada
                        config = aai.TranscriptionConfig(
                            speech_models=["universal-3-pro", "universal-2"],
                            language_code="es"
                        )
                        
                        transcript = transcriber.transcribe(path, config=config)
                        
                        if transcript.status == aai.TranscriptStatus.error:
                            st.error(f"Error: {transcript.error}")
                        else:
                            st.success("¡Completado!")
                            st.text_area("Texto extraído:", transcript.text, height=200, key=f"area_{i}")
                    except Exception as e:
                        st.error(f"Error inesperado: {e}")
                    finally:
                        os.remove(path)
        st.balloons()
