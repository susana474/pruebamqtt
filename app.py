import os
import json
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Cargar las credenciales de Firebase desde las variables de entorno
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if firebase_credentials:
    creds_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(creds_dict)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://tu-proyecto-default-rtdb.firebaseio.com/"
    })
else:
    print("⚠️ ERROR: No se encontró la clave de Firebase en las variables de entorno.")

# Ruta para recibir JSON y guardarlo en Firebase
@app.route('/guardar', methods=['POST'])
def guardar_en_firebase():
    try:
        data = request.get_json()  # Recibe los datos en JSON
        ref = db.reference("/datos_recibidos")  # Ruta en Firebase
        nueva_ref = ref.push(data)  # Guarda los datos con un ID único
        return jsonify({"message": "Datos guardados", "id": nueva_ref.key}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Prueba básica
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API funcionando"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

