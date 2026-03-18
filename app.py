import streamlit as st
import assemblyai as aai
import tempfile
import os
import zipfile
import io

# 1. Configuración de la página
st.set_page_config(page_title="Transcriptor Pro", page_icon="🎬", layout="wide")

# Inicializamos la variable para limpiar la página al hacer un "Nuevo Trabajo"
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

def reiniciar_app():
    st.session_state["uploader_key"] += 1
    # st.rerun() reinicia la app para limpiar la pantalla
    st.rerun()

# --- Interfaz de Usuario ---
st.title("🎬 Transcriptor de Videos")

# Botón de reinicio en la parte superior
col_title, col_reset = st.columns([4, 1])
with col_reset:
    st.button("🔄 Nuevo Trabajo", on_click=reiniciar_app, use_container_width=True)

st.write("Sube tus clips para convertirlos a texto.")

# 2. Configuración de la API
try:
    aai.settings.api_key = st.secrets["ASSEMBLYAI_API_KEY"]
except:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")

# 3. Subida de archivos
uploaded_files = st.file_uploader(
    "Selecciona uno o varios videos", 
    type=["mp4", "mov", "avi", "mkv"], 
    accept_multiple_files=True,
    key=f"uploader_{st.session_state['uploader_key']}"
)

if uploaded_files:
    if st.button("🚀 Empezar Transcripción", use_container_width=True):
        
        # Diccionario para guardar todos los textos y meterlos al ZIP luego
        textos_para_zip = {}
        
        for i, file in enumerate(uploaded_files):
            with st.expander(f"🎥 Archivo: {file.name}", expanded=True):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.info("Video Original")
                    st.video(file)
                
                with col2:
                    st.info("Transcripción de la IA")
                    with st.spinner("Procesando audio..."):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                            tmp.write(file.getvalue())
                            path = tmp.name
                        
                        try:
                            transcriber = aai.Transcriber()
                            config = aai.TranscriptionConfig(
                                speech_models=["universal-3-pro", "universal-2"],
                                language_code="es"
                            )
                            transcript = transcriber.transcribe(path, config=config)
                            
                            if transcript.status == aai.TranscriptStatus.error:
                                st.error(f"Error: {transcript.error}")
                            else:
                                st.text_area("Texto extraído:", transcript.text, height=300, key=f"area_{i}")
                                
                                # Botón individual (opcional, por si acaso)
                                st.download_button(
                                    label="📄 Descargar este TXT",
                                    data=transcript.text,
                                    file_name=f"transcripcion_{file.name}.txt",
                                    mime="text/plain",
                                    key=f"btn_{i}"
                                )
                                
                                # Guardamos el texto en nuestra memoria para el ZIP
                                nombre_txt = f"transcripcion_{file.name}.txt"
                                textos_para_zip[nombre_txt] = transcript.text
                                
                        except Exception as e:
                            st.error(f"Error inesperado: {e}")
                        finally:
                            if os.path.exists(path):
                                os.remove(path)
        
        # --- CREACIÓN DEL ARCHIVO ZIP ---
        # Si logramos transcribir al menos un archivo con éxito, creamos el ZIP
        if textos_para_zip:
            st.success("✨ ¡Todas las transcripciones han finalizado con éxito!")
            
            # Creamos un archivo ZIP en la memoria virtual
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for nombre_archivo, contenido in textos_para_zip.items():
                    zip_file.writestr(nombre_archivo, contenido)
            
            # Mostramos el Gran Botón para descargar el ZIP
            st.download_button(
                label="📦 DESCARGAR TODAS LAS TRANSCRIPCIONES (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="todas_las_transcripciones.zip",
                mime="application/zip",
                type="primary", # Le da un color destacado al botón
                use_container_width=True
            )
            
            st.balloons()
