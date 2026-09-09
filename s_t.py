import glob
import os
import time

from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from googletrans import Translator
from gtts import gTTS
from PIL import Image
import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events

# Configuración básica de la app
st.set_page_config(
    page_title="GlobalVoice - Cabina de Inmersión y Acentos", layout="wide"
)

os.makedirs("temp", exist_ok=True)


# Limpieza de archivos antiguos
def remove_old_files(days=7):
    mp3_files = glob.glob("temp/*.mp3")
    now = time.time()
    n_days = days * 86400
    for f in mp3_files:
        if os.stat(f).st_mtime < now - n_days:
            try:
                os.remove(f)
            except OSError:
                pass


remove_old_files(7)

# --- CABECERA E INTERFAZ ---
st.title("🌐 GlobalVoice: Entrenador de Acentos e Inmersión")
st.caption(
    "Traduce en tiempo real por voz y pon a prueba tu oído escuchando cómo suena"
    " el idioma en distintas partes del mundo."
)

col_img, col_info = st.columns([1, 2])

with col_img:
    try:
        image = Image.open("OIG7.jpg")
        st.image(image, width=260, caption="Simulador Multimodal")
    except FileNotFoundError:
        st.info("📷 Coloca la imagen 'OIG7.jpg' en la carpeta de la app.")

with col_info:
    st.subheader("💡 ¿Cómo usar esta cabina?")
    st.write("""
    1. Presiona **Escuchar 🎤** y habla claramente por tu micrófono.
    2. Revisa el texto reconocido en pantalla.
    3. Elige el idioma al que deseas traducirlo.
    4. **¡Lo más divertido!** Elige la región para escuchar el acento nativo específico (Reino Unido, Australia, EE.UU., etc.).
    """)

st.divider()

# --- RECONOCIMIENTO DE VOZ (BOKEH) ---
st.subheader("1. Captura de Voz")

stt_button = Button(label=" Escuchar 🎤", width=280, height=45)
stt_button.js_on_event(
    "button_click",
    CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'es-ES';

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    
    recognition.onend = function() {
        console.log("Reconocimiento detenido");
    }
    
    recognition.start();
"""),
)

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0,
)

# --- MAPEOS PERSONALIZADOS DE IDIOMAS Y ACENTOS ---
IDIOMAS = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Alemán": "de",
    "Italiano": "it",
    "Portugués": "pt",
    "Mandarín": "zh-cn",
    "Japonés": "ja",
    "Coreano": "ko",
}

ACENTOS_TLD = {
    "Defecto / Estándar": "com",
    "Reino Unido 🇬🇧": "co.uk",
    "Estados Unidos 🇺🇸": "com",
    "Canadá 🇨🇦": "ca",
    "Australia 🇦🇺": "com.au",
    "Irlanda 🇮🇪": "ie",
    "Sudáfrica 🇿🇦": "co.za",
    "Francia 🇫🇷": "fr",
    "Brasil 🇧🇷": "com.br",
    "México / Latam 🇲🇽": "com.mx",
}

# --- PROCESAMIENTO DE TRADUCCIÓN ---
if result and "GET_TEXT" in result:
    captured_text = result.get("GET_TEXT")
    st.success(f"🗣️ **Texto detectado:** {captured_text}")

    st.subheader("2. Configuración de Traducción y Acento")

    col_lang1, col_lang2, col_accent = st.columns(3)

    with col_lang1:
        in_lang_name = st.selectbox(
            "Idioma de origen:", list(IDIOMAS.keys()), index=0
        )
    with col_lang2:
        out_lang_name = st.selectbox(
            "Idioma de destino:", list(IDIOMAS.keys()), index=1
        )
    with col_accent:
        accent_name = st.selectbox("Acento Regional (TLD):", list(ACENTOS_TLD.keys()))

    display_output_text = st.checkbox("Mostrar texto traducido", value=True)

    if st.button("🚀 Traducir y Generar Audio", type="primary"):
        with st.spinner("Traduciendo y sintetizando voz con el acento seleccionado..."):
            try:
                translator = Translator()

                src_code = IDIOMAS[in_lang_name]
                dest_code = IDIOMAS[out_lang_name]
                tld_code = ACENTOS_TLD[accent_name]

                # Traducción
                translation = translator.translate(
                    captured_text, src=src_code, dest=dest_code
                )
                translated_text = translation.text

                # Síntesis de voz con gTTS
                tts = gTTS(translated_text, lang=dest_code, tld=tld_code, slow=False)

                # Nombre de archivo seguro
                safe_file_id = "".join(
                    c for c in captured_text[:10] if c.isalnum()
                ).lower()
                if not safe_file_id:
                    safe_file_id = "audio"
                file_path = f"temp/{safe_file_id}_{int(time.time())}.mp3"

                tts.save(file_path)

                # Reproducción
                st.divider()
                st.subheader("🔊 Resultado Auditivo")

                if display_output_text:
                    st.info(f"**Traducción ({out_lang_name}):** {translated_text}")

                with open(file_path, "rb") as f:
                    audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")

            except Exception as e:
                st.error(f"Error durante la traducción o generación de audio: {e}")

else:
    st.info("👆 Haz clic en **Escuchar 🎤** para empezar a dictar tu frase.")


        
    


