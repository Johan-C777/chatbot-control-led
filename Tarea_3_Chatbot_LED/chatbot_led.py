import streamlit as st
import speech_recognition as sr
import unicodedata

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

import paho.mqtt.publish as publish

BROKER = "broker.hivemq.com"
TOPIC = "umng/embebidos/chatbot_led/johan_8f21c6"

frases = [
    # ENCENDER
    "enciende el led",
    "prende el led",
    "prender led",
    "enciende la luz",
    "prende la luz",
    "activa el led",
    "activa la luz",
    "quiero prender el led",
    "quiero encender el led",
    "puedes prender el led",
    "enciende por favor",
    "prende por favor",
    "activar led",
    "quiero prender la luz",

    # APAGAR
    "apaga el led",
    "apagar led",
    "apaga la luz",
    "desactiva el led",
    "desactiva la luz",
    "quiero apagar el led",
    "puedes apagar el led",
    "apaga por favor",
    "desconecta el led",
    "desactivar led",
    "quiero apagar la luz",
    "apágalo",
    "apagar la luz",
    "quiero que apagues el led"
]

etiquetas = [
    "encender", "encender", "encender", "encender",
    "encender", "encender", "encender", "encender",
    "encender", "encender", "encender", "encender",
    "encender", "encender",

    "apagar", "apagar", "apagar", "apagar",
    "apagar", "apagar", "apagar", "apagar",
    "apagar", "apagar", "apagar", "apagar",
    "apagar", "apagar"
]

def normalizar(texto):
    texto = texto.lower().strip()

    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return texto


frases = [normalizar(frase) for frase in frases]

modelo = Pipeline([
    (
        "vectorizador",
        TfidfVectorizer(
            ngram_range=(1, 2)
        )
    ),
    (
        "clasificador",
        LogisticRegression(
            max_iter=1000
        )
    )
])

modelo.fit(frases, etiquetas)

def enviar_comando(comando):

    publish.single(
        TOPIC,
        payload=comando,
        hostname=BROKER,
        port=1883
    )

def interpretar_chat(texto):

    texto = normalizar(texto)

    probabilidades = modelo.predict_proba([texto])[0]

    indice = probabilidades.argmax()

    confianza = probabilidades[indice]

    intencion = modelo.classes_[indice]


    if confianza < 0.50:

        return (
            "No entendí el comando.",
            "ninguno",
            confianza
        )


    if intencion == "encender":

        enviar_comando("ON")

        return (
            "LED encendido.",
            "encender",
            confianza
        )


    if intencion == "apagar":

        enviar_comando("OFF")

        return (
            "LED apagado.",
            "apagar",
            confianza
        )

def procesar(texto):

    st.write("### Tú")
    st.info(texto)

    try:

        respuesta, intencion, confianza = interpretar_chat(texto)

        st.write("### Chatbot")
        st.success(respuesta)

        st.write(
            "**Intención detectada:**",
            intencion
        )

        st.write(
            "**Confianza:**",
            f"{confianza * 100:.1f}%"
        )

    except Exception as error:

        st.error(
            f"Error enviando comando MQTT: {error}"
        )

st.title("💡 Control de LED por Voz")

st.write(
    "Chatbot entrenado para reconocer "
    "órdenes de encendido y apagado."
)

st.divider()

st.subheader("1. Prueba por texto")

texto_manual = st.text_input(
    "Escribe un comando:",
    placeholder="Ejemplo: prende el LED"
)

if st.button("Enviar comando escrito"):

    if texto_manual:
        procesar(texto_manual)


st.divider()

st.subheader("2. Control por voz")

st.write(
    "Pulsa el micrófono, habla y después "
    "finaliza la grabación."
)

audio = st.audio_input(
    "🎤 Grabar comando de voz",
    sample_rate=16000
)


if audio is not None:

    st.audio(audio)

    audio_bytes = audio.getvalue()

    audio_id = hash(audio_bytes)

    if (
        "ultimo_audio" not in st.session_state
        or st.session_state.ultimo_audio != audio_id
    ):

        st.session_state.ultimo_audio = audio_id

        recognizer = sr.Recognizer()

        try:

            with sr.AudioFile(audio) as source:

                datos_audio = recognizer.record(source)


            with st.spinner("Reconociendo voz..."):

                texto = recognizer.recognize_google(
                    datos_audio,
                    language="es-CO"
                )


            procesar(texto)


        except sr.UnknownValueError:

            st.error(
                "No se pudo entender el audio. "
                "Habla más cerca del micrófono."
            )


        except sr.RequestError as error:

            st.error(
                "Error en el servicio de reconocimiento: "
                + str(error)
            )


        except Exception as error:

            st.error(
                "Error inesperado: "
                + str(error)
            )