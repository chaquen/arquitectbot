from flask import Flask
from flasgger import Swagger
from app.interfaces.flask_controller import bp

def create_app():
    app = Flask(__name__)
    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "API de Componentes de Arquitectura",
            "description": "Documentación interactiva de la API de componentes.",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": ["http"],
    })
    app.register_blueprint(bp)
    return app
