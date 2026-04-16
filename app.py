import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

# ================= VARIABLES =================
Expert = " "
profile_imgenh = " "

# ================= FUNCIONES =================
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# ================= CONFIG UI =================
st.set_page_config(page_title='Tablero Inteligente', layout="wide")

st.title('🧠 Tablero Inteligente')

st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Drawing_of_a_drawing.JPG/960px-Drawing_of_a_drawing.JPG",
    caption="Ejemplo de boceto",
    width=600
)

st.subheader("Dibuja un boceto y presiona el botón para analizarlo")

# ================= SIDEBAR =================
st.sidebar.title("⚙️ Configuración")

stroke_width = st.sidebar.slider('Ancho de línea', 1, 30, 5)

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 API Key")
ke = st.sidebar.text_input('Ingresa tu clave', type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Acerca de")
st.sidebar.info(
    "Esta aplicación permite analizar un boceto dibujado y describirlo usando IA."
)

# ================= CANVAS =================
st.markdown("### ✏️ Área de dibujo")

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color="#000000",
    background_color='#FFFFFF',
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas",
)

# ================= API SETUP =================
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# ================= BOTÓN =================
analyze_button = st.button("🔍 Analizar imagen")

# ================= LÓGICA =================
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando imagen... ⏳"):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")

        prompt_text = "Describe en español brevemente la imagen"

        try:
            message_placeholder = st.empty()

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            if response.choices[0].message.content is not None:
                result = response.choices[0].message.content
                message_placeholder.markdown("### 🧾 Resultado")
                st.success(result)

                if Expert == profile_imgenh:
                    st.session_state.mi_respuesta = result

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

# ================= VALIDACIONES =================
else:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu API key.")
    elif canvas_result.image_data is None:
        st.info("✏️ Dibuja algo en el tablero para analizarlo.")
