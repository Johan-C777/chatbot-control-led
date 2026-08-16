from machine import Pin
import network
import time


# ==========================================
# WIFI
# ==========================================

SSID = "Red"
PASSWORD = "Contrasena"


# ==========================================
# MQTT
# ==========================================

BROKER = "broker.hivemq.com"

TOPIC = b"umng/embebidos/chatbot_led/johan_8f21c6"


# ==========================================
# LED
# ==========================================

led = Pin(25, Pin.OUT)

led.off()


# ==========================================
# CONEXION WIFI
# ==========================================

print("Conectando a WiFi...")


wifi = network.WLAN(
    network.STA_IF
)


wifi.active(False)

time.sleep(1)


wifi.active(True)

time.sleep(1)


try:

    wifi.disconnect()

except:

    pass


wifi.connect(
    SSID,
    PASSWORD
)


while not wifi.isconnected():

    print(".", end="")

    time.sleep(0.5)


print()

print("WiFi conectado")

print(
    "IP:",
    wifi.ifconfig()[0]
)


# ==========================================
# MQTT
# ==========================================

try:

    from umqtt.simple import MQTTClient


except ImportError:

    import mip

    print(
        "Instalando MQTT..."
    )

    mip.install(
        "umqtt.simple"
    )

    from umqtt.simple import MQTTClient


# ==========================================
# RECIBIR COMANDO
# ==========================================

def recibir_mensaje(
    topic,
    mensaje
):

    comando = (
        mensaje
        .decode()
        .strip()
        .upper()
    )


    print(
        "Comando:",
        comando
    )


    if comando == "ON":

        led.on()

        print(
            "LED ENCENDIDO"
        )


    elif comando == "OFF":

        led.off()

        print(
            "LED APAGADO"
        )


# ==========================================
# CONEXION MQTT
# ==========================================

print(
    "Conectando a MQTT..."
)


client = MQTTClient(

    client_id=(
        b"esp32_chatbot_johan"
    ),

    server=BROKER,

    port=1883,

    keepalive=60
)


client.set_callback(
    recibir_mensaje
)


client.connect()


client.subscribe(
    TOPIC
)


print(
    "MQTT conectado"
)

print(
    "Esperando comandos de voz..."
)


# ==========================================
# LOOP
# ==========================================

ultimo_ping = time.ticks_ms()


while True:

    try:

        client.check_msg()


        if time.ticks_diff(
            time.ticks_ms(),
            ultimo_ping
        ) > 30000:

            client.ping()

            ultimo_ping = (
                time.ticks_ms()
            )


    except Exception as error:

        print(
            "Error MQTT:",
            error
        )


    time.sleep_ms(50)