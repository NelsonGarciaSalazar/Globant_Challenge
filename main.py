from flask import Flask
from flask_cors import CORS
from api.routes import router

app = Flask(__name__)
CORS(app)  # Permite CORS para todos los orígenes y rutas
app.register_blueprint(router)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

