from flask import Flask
from flasgger import Swagger
from app.interfaces.flask_controller import bp

def create_app():
    app = Flask(__name__)
    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "ArquitectBot – API del Modelo de Grafo",
            "description": "Importación y consulta del modelo de arquitectura basado en JSON.",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": ["http"],
    })
    app.register_blueprint(bp)
    return app
