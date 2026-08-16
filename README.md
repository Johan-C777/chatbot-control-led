# Control de LED por Voz mediante Chatbot y ESP32

## Descripción

En este proyecto se desarrolló un sistema para controlar un LED conectado a un ESP32 mediante comandos de lenguaje natural.

El sistema permite recibir órdenes por texto y por voz, identificar la intención del usuario mediante un modelo de clasificación entrenado y enviar el comando correspondiente al ESP32 mediante comunicación MQTT.

Las dos acciones principales implementadas son:

* Encender el LED.
* Apagar el LED.

## Objetivo

Desarrollar y entrenar un chatbot capaz de interpretar diferentes formas de solicitar el encendido o apagado de un LED y utilizar el resultado para controlar físicamente una salida digital de un ESP32.

## Arquitectura del sistema

El funcionamiento general del proyecto es:

```text
Usuario
   |
   | Texto / Voz
   v
Interfaz Streamlit
   |
   v
Reconocimiento de voz
   |
   v
Chatbot entrenado
   |
   | Intención
   | ENCENDER / APAGAR
   v
MQTT
   |
   v
ESP32
   |
   v
LED
```

El procesamiento del chatbot se realiza en el computador, mientras que el ESP32 se encarga del control físico del LED.

## Herramientas utilizadas

* Python
* Visual Studio Code
* Streamlit
* SpeechRecognition
* Scikit-learn
* Paho MQTT
* MicroPython
* Thonny
* ESP32
* MQTT
* HiveMQ Public Broker

## Conexión física

Para el montaje se utilizó un LED conectado al GPIO 25 del ESP32.

| Elemento    | Conexión      |
| ----------- | ------------- |
| LED         | GPIO 25       |
| Resistencia | 220 Ω o 330 Ω |
| Tierra      | GND           |

La conexión utilizada es:

```text
GPIO25
   |
Resistencia
   |
   LED
   |
  GND
```

## Chatbot

El chatbot fue desarrollado en Python y utiliza un modelo de clasificación para identificar la intención presente en la frase recibida.

Se definieron dos clases:

```text
encender
apagar
```

Para entrenar el modelo se utilizaron diferentes frases asociadas a cada intención.

### Ejemplos para encender

```text
enciende el led
prende el led
enciende la luz
prende la luz
activa el led
quiero prender el led
quiero encender el led
puedes prender el led
```

### Ejemplos para apagar

```text
apaga el led
apaga la luz
desactiva el led
quiero apagar el led
puedes apagar el led
desconecta el led
quiero apagar la luz
```

## Entrenamiento

Para el procesamiento del lenguaje se utilizó `TfidfVectorizer`.

Este método transforma las frases en características numéricas que pueden ser procesadas por un algoritmo de clasificación.

Posteriormente se utilizó `LogisticRegression` para aprender a diferenciar las intenciones de encendido y apagado.

El modelo se construye mediante:

```python
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
```

El entrenamiento se realiza mediante:

```python
modelo.fit(frases, etiquetas)
```

De esta manera el sistema no depende únicamente de una frase exacta, sino que puede clasificar diferentes expresiones relacionadas con las acciones aprendidas.

## Interfaz gráfica

Se desarrolló una interfaz mediante Streamlit.

La aplicación contiene dos métodos de entrada.

### Entrada mediante texto

El usuario puede escribir una instrucción como:

```text
prende el led
```

El chatbot procesa la frase y determina la intención:

```text
encender
```

### Entrada mediante voz

La interfaz permite grabar una orden mediante el micrófono.

El audio capturado es convertido a texto mediante reconocimiento de voz y posteriormente enviado al mismo modelo de clasificación utilizado para los comandos escritos.

Por ejemplo:

```text
Usuario:
"Prende el LED"

          |
          v

Reconocimiento de voz:
"prende el led"

          |
          v

Chatbot:
encender
```

## Nivel de confianza

El clasificador obtiene una probabilidad para cada posible intención.

Se utiliza un nivel mínimo de confianza para evitar ejecutar órdenes cuando el chatbot no puede determinar correctamente la intención.

Si la confianza no supera el umbral establecido, el sistema responde:

```text
No entendí el comando.
```

## Comunicación MQTT

Una vez identificada la intención, el computador envía un mensaje MQTT.

Se utilizó el broker público:

```text
broker.hivemq.com
```

El sistema utiliza dos comandos:

```text
ON
OFF
```

El flujo de comunicación es:

```text
Chatbot
   |
   | ON / OFF
   v
Broker MQTT
   |
   v
ESP32
```

Para enviar el comando desde Python se utiliza Paho MQTT.

```python
publish.single(
    TOPIC,
    payload=comando,
    hostname=BROKER,
    port=1883
)
```

## Programa del ESP32

El ESP32 fue programado utilizando MicroPython.

El microcontrolador realiza las siguientes funciones:

1. Configura el GPIO 25 como salida.
2. Se conecta a una red Wi-Fi.
3. Se conecta al broker MQTT.
4. Se suscribe al tópico correspondiente.
5. Espera comandos enviados por el chatbot.
6. Controla el LED dependiendo del mensaje recibido.

## Control del LED

Cuando el ESP32 recibe:

```text
ON
```

ejecuta:

```python
led.on()
```

y el LED se enciende.

Cuando recibe:

```text
OFF
```

ejecuta:

```python
led.off()
```

y el LED se apaga.

## Funcionamiento completo

### Encendido

```text
"Prende el LED"
       |
       v
Reconocimiento de voz
       |
       v
Chatbot
       |
       v
Intención: encender
       |
       v
MQTT: ON
       |
       v
ESP32
       |
       v
LED ENCENDIDO
```

### Apagado

```text
"Apaga el LED"
       |
       v
Reconocimiento de voz
       |
       v
Chatbot
       |
       v
Intención: apagar
       |
       v
MQTT: OFF
       |
       v
ESP32
       |
       v
LED APAGADO
```

## Ejecución

### 1. ESP32

Se ejecuta `main.py` en el ESP32 mediante Thonny.

El dispositivo se conecta a Wi-Fi y posteriormente al broker MQTT.

La consola muestra:

```text
WiFi conectado
MQTT conectado
Esperando comandos de voz...
```

### 2. Chatbot

Desde el computador se ejecuta:

```bash
python -m streamlit run chatbot_led.py
```

Se abre la interfaz web local de Streamlit.

Desde allí es posible utilizar la entrada escrita o el micrófono para enviar órdenes al chatbot.

## Archivos del proyecto

### `chatbot_led.py`

Contiene:

* Interfaz Streamlit.
* Captura de audio.
* Reconocimiento de voz.
* Datos de entrenamiento.
* Modelo de clasificación.
* Identificación de intenciones.
* Comunicación MQTT.

### `main.py`

Programa MicroPython ejecutado en el ESP32.

Contiene:

* Configuración GPIO.
* Conexión Wi-Fi.
* Conexión MQTT.
* Recepción de mensajes.
* Control físico del LED.

### `requirements.txt`

Contiene las dependencias necesarias para ejecutar el chatbot en el computador.

## Evidencias

Las evidencias experimentales del funcionamiento se encuentran en la carpeta:

```text
evidencias/
```

Se documentarán pruebas correspondientes a:

* Interfaz del chatbot.
* Reconocimiento del comando por voz.
* Comando de encendido.
* LED físicamente encendido.
* Comando de apagado.
* LED físicamente apagado.
* Recepción de comandos MQTT en el ESP32.

## Resultado

Se implementó una arquitectura que permite integrar procesamiento de lenguaje natural, reconocimiento de voz, comunicación mediante MQTT y un sistema embebido.

El computador realiza el procesamiento del lenguaje y determina la intención del usuario, mientras que el ESP32 recibe únicamente el comando final y controla la salida física.

## Conclusión

La práctica permitió aplicar conceptos de sistemas embebidos, procesamiento de lenguaje natural, reconocimiento de voz y comunicación IoT.

La separación entre el procesamiento realizado en el computador y el control realizado por el ESP32 permite desarrollar una arquitectura modular en la que nuevos comandos o dispositivos pueden incorporarse posteriormente sin modificar completamente el sistema.
