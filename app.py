import streamlit as st
import assemblyai as aai
import tempfile
import os

# Configuración visual de la página
st.set_page_config(page_title="Video a Texto", page_icon="📹")
st.title("📹 Transcriptor de Video a Texto")
st.write("Sube tu videoclip y la IA extraerá todo lo que se dice.")

# Aquí pondremos tu clave de API (luego la configuramos en la nube)
# Para probar en tu PC, puedes cambiar st.secrets... por "TU_API_KEY_DE_ASSEMBLYAI" entre comillas
aai.settings.api_key = st.secrets["ASSEMBLYAI_API_KEY"]

# Botón para subir el video
uploaded_file = st.file_uploader("Elige un archivo de video", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    st.video(uploaded_file) # Muestra el video en la página
    
    if st.button("Transcribir Video"):
        with st.spinner("Transcribiendo... Esto puede tardar unos minutos dependiendo del tamaño del video."):
            # Guardar el archivo temporalmente para que la IA lo lea
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(uploaded_file.read())
                temp_video_path = temp_video.name
            
            try:
                # Enviar a la IA (configurado para entender Español)
                transcriber = aai.Transcriber()
                config = aai.TranscriptionConfig(language_code="es") 
                transcript = transcriber.transcribe(temp_video_path, config=config)
                
                if transcript.status == aai.TranscriptStatus.error:
                    st.error(f"Error en la transcripción: {transcript.error}")
                else:
                    st.success("¡Transcripción completada con éxito!")
                    st.text_area("Texto del video:", transcript.text, height=300)
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
            finally:
                # Limpiar el archivo temporal
                os.remove(temp_video_path)