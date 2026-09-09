import glob
import os
import time

from deep_translator import GoogleTranslator
from gtts import gTTS
from PIL import Image
import streamlit as st

# Configuración básica de la app
st.set_page_config(
    page_title="GlobalVoice - Cabina de Inmersión y Acentos, diviertete para hablar como un estereotipo bro", layout="wide"
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
st.title("🌐 GlobalVoice: Entrenador de Acentos Chistosos e Inmersión")
st.caption(
    "Traduce en tiempo real y pon a prueba tu oído escuchando cómo suena"
    " el idioma en distintas partes del mundo, bueno pa' divertirse con los amigos."
)

col_img, col_info = st.columns([1, 2])

with col_img:
    try:
        image = Image.open("Fun_italian_man.jpg")
        st.image(image, width=260, caption="Simulador Multimodal de acentos para el trabajo del profe, profe pongame 5 de una porfa")
    except FileNotFoundError:
        st.info("📷 Coloca la imagen 'OIG7.jpg' en la carpeta de la app.")

with col_info:
    st.subheader("💡 ¿Cómo usar esta monda'?")
    st.write("""
    1. Ingresa el texto o usa las opciones de entrada.
    2. Elige el idioma de origen y de destino.
    3. Selecciona el acento regional que deseas practicar, entre más charro mejor.
    4. Presiona **Traducir y Generar Audio**.
    """)

st.divider()

# --- DICCIONARIOS DE IDIOMAS Y ACENTOS ---
IDIOMAS = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Alemán": "de",
    "Italiano": "it",
    "Portugués": "pt",
    "Mandarín": "zh-CN",
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

# --- ENTRADA DE TEXTO ---
st.subheader("1. Cajita para escribir tus cosas")
captured_text = st.text_input(
    "Escribe el texto a traducir:", value="Hola, ¿cómo estás?"
)

# --- CONFIGURACIÓN Y PROCESAMIENTO ---
st.subheader("2. Espacio para colocar los acentos, si es Italiano va para el cielo D1")

col_lang1, col_lang2, col_accent = st.columns(3)

with col_lang1:
    in_lang_name = st.selectbox("Idioma de origen:", list(IDIOMAS.keys()), index=0)
with col_lang2:
    out_lang_name = st.selectbox(
        "Idioma de destino:", list(IDIOMAS.keys()), index=1
    )
with col_accent:
    accent_name = st.selectbox("Acento Regional (TLD):", list(ACENTOS_TLD.keys()))

display_output_text = st.checkbox("Mostrar texto traducido", value=True)

if st.button("🚀 Presiona y cagate de la risa", type="primary"):
    if not captured_text.strip():
        st.warning("Por favor ingresa un texto válido.")
    else:
        with st.spinner(
            "Traduciendo y sintetizando voz con el acento seleccionado..."
        ):
            try:
                src_code = IDIOMAS[in_lang_name]
                dest_code = IDIOMAS[out_lang_name]
                tld_code = ACENTOS_TLD[accent_name]

                # Traducción mediante deep-translator
                translated_text = GoogleTranslator(
                    source=src_code, target=dest_code
                ).translate(captured_text)

                # Síntesis de voz con gTTS
                # Se limpia el código para gTTS (ej. 'zh-CN' a 'zh-cn')
                gtts_lang = dest_code.lower()
                tts = gTTS(
                    translated_text, lang=gtts_lang, tld=tld_code, slow=False
                )

                file_path = f"temp/audio_{int(time.time())}.mp3"
                tts.save(file_path)

                # Resultado
                st.divider()
                st.subheader("🔊 Resultado Auditivo, para deleitar incluso a sordos")

                if display_output_text:
                    st.info(
                        f"**Traducción ({out_lang_name}):** {translated_text}"
                    )

                with open(file_path, "rb") as f:
                    audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")

            except Exception as e:
                st.error(f"Error al procesar: {e}")


