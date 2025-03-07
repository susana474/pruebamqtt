import json
import time
import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify

# Configuración de la aplicación Flask
app = Flask(__name__)

# Configuración de MQTT Hive
MQTT_BROKER = "broker.hivemq.com"  # Broker público de HiveMQ
MQTT_PORT = 1883
MQTT_TOPIC = "mi_aplicacion/datos"
MQTT_CLIENT_ID = f"python-mqtt-{time.time()}"

# Función de conexión al broker MQTT
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado a MQTT Broker!")
        else:
            print(f"Error de conexión, código de retorno {rc}")

    client = mqtt.Client(MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client

# Función para publicar mensaje en MQTT
def publish(client, topic, msg):
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Mensaje enviado a {topic}: {msg}")
    else:
        print(f"Error al enviar mensaje a {topic}")

# Iniciar cliente MQTT
mqtt_client = connect_mqtt()
mqtt_client.loop_start()

# Ruta para recibir datos JSON
@app.route('/recibir_datos', methods=['POST'])
def recibir_datos():
    try:
        # Recibir datos JSON de la interfaz
        datos = request.json
        
        if not datos:
            return jsonify({"status": "error", "message": "No se recibieron datos"}), 400
        
        # Aquí puedes procesar los datos con IA si lo necesitas
        # Por ejemplo: resultado = procesar_con_ia(datos)
        
        # Para este ejemplo simplemente pasamos los datos recibidos
        resultado = datos
        
        # Convertir a string JSON para enviar por MQTT
        mensaje = json.dumps(resultado)
        
        # Publicar en MQTT Hive
        publish(mqtt_client, MQTT_TOPIC, mensaje)
        
        return jsonify({"status": "success", "message": "Datos publicados en MQTT"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Función opcional: procesar con IA (implementar según necesidades)
def procesar_con_ia(datos):
    # Aquí irían las llamadas a tu modelo de IA
    # Por ejemplo, usando TensorFlow, PyTorch, o una API externa
    
    # Este es solo un ejemplo de procesamiento simple
    resultado = datos.copy()
    resultado["procesado"] = True
    resultado["timestamp"] = time.time()
    
    return resultado

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
