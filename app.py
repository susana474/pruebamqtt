from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
import paho.mqtt.client as mqtt
import os
from pathlib import Path

# Modelo para validar datos de entrada
class MessageData(BaseModel):
    message: str

# Configuración de FastAPI
app = FastAPI(title="API MQTT Publisher")

# Configuración del broker MQTT
BROKER = "broker.mqtt.cool"
PORT = 1883  # Puerto estándar para MQTT
TOPIC = "mi/topico/mqtt"
CLIENT_ID = "MQTT_Publisher_Client"

# Callbacks para el cliente MQTT
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Conectado al broker MQTT ({BROKER})")
    else:
        print(f"⚠️ Error al conectar: {rc}")

def on_disconnect(client, userdata, rc, properties=None):
    print(f"Desconectado con código: {rc}")

# Crear cliente MQTT
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

# Conectar al broker de forma más segura
try:
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()  # Iniciar loop en segundo plano
except Exception as e:
    print(f"⚠️ Error al conectar con el broker MQTT: {e}")

# Endpoint raíz para GET
@app.get("/")
async def root_get(message: str = None):
    """Endpoint GET que acepta parámetro de consulta"""
    if message:
        try:
            result = mqtt_client.publish(TOPIC, message)
            if result.rc != 0:
                raise HTTPException(status_code=500, detail=f"Error al publicar: {result.rc}")
            return {"status": "success", "message": f"Publicado en MQTT: {message}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    else:
        return {"message": "Bienvenido a la API MQTT Publisher. Usa ?message=TuMensaje para publicar"}

# Endpoint raíz para POST
@app.post("/")
async def root_post(data: MessageData = None, request: Request = None):
    """Endpoint POST que acepta JSON"""
    try:
        # Si se envió un objeto MessageData
        if data and data.message:
            message = data.message
        # Si no, intentamos leer el cuerpo de la solicitud
        else:
            body = await request.json()
            message = body.get("message")
            
        if not message:
            return {"status": "error", "message": "No se proporcionó un mensaje"}
            
        result = mqtt_client.publish(TOPIC, message, qos=1, retain=True)

        if result.rc != 0:
            raise HTTPException(status_code=500, detail=f"Error al publicar: {result.rc}")
        return {"status": "success", "message": f"Publicado en MQTT: {message}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint para favicon
@app.get("/favicon.ico")
async def favicon():
    """Maneja la solicitud de favicon.ico"""
    favicon_path = Path("static/favicon.ico")
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return Response(status_code=204)

# Endpoint original para publicar
@app.post("/publish/")
async def publish_message(data: MessageData):
    """Recibe un mensaje por API y lo publica en MQTT"""
    try:
        result = mqtt_client.publish(TOPIC, 1)
        if result.rc != 0:
            raise HTTPException(status_code=500, detail=f"Error al publicar: {result.rc}")
        return {"status": "success", "message": f"Publicado en MQTT: {data.message}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Limpieza al cerrar la aplicación
@app.on_event("shutdown")
def shutdown_event():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("Cliente MQTT desconectado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
