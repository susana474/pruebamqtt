from fastapi import FastAPI
import paho.mqtt.client as mqtt
import os

# Configuración de FastAPI
app = FastAPI(title="API MQTT Publisher")

# Configuración del broker MQTT (HiveMQ público)
BROKER = "	broker.emqx.io"
PORT = 1883
TOPIC = "mi/topico/mqtt"  # Cambia esto a un tópico personalizado
CLIENT_ID = "MQTT_Publisher_Client"

# Crear cliente MQTT
mqtt_client = mqtt.Client(CLIENT_ID)

# Conectar al broker
mqtt_client.connect(BROKER, PORT, 60)

# Endpoint para recibir datos y publicarlos en MQTT
@app.post("/publish/")
async def publish_message(message: str):
    """Recibe un mensaje por API y lo publica en MQTT"""
    mqtt_client.publish(TOPIC, message)
    return {"message": f"Publicado en MQTT: {message}"}

# Ejecutar el servidor con uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
