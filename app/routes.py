from flask import Blueprint, jsonify, request
from app.controllers import ComponentController
from flasgger import swag_from

bp = Blueprint('main', __name__)
controller = ComponentController()

@bp.route('/components', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Lista de componentes',
            'examples': {
                'application/json': [
                    {'id': 1, 'name': 'API Gateway', 'type': 'Service', 'description': 'Main API Gateway'}
                ]
            }
        }
    }
})
def get_components():
    return controller.get_all_components()

@bp.route('/components', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'type': {'type': 'string'},
                    'description': {'type': 'string'}
                },
                'required': ['name', 'type']
            }
        }
    ],
    'responses': {
        201: {'description': 'Componente creado'},
        400: {'description': 'Error de validación'}
    }
})
def create_component():
    data = request.get_json()
    return controller.create_component(data)

@bp.route('/components/<int:id>', methods=['GET'])
@swag_from({
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Componente encontrado'},
        404: {'description': 'No encontrado'}
    }
})
def get_component(id):
    return controller.get_component(id)

@bp.route('/components/<int:id>', methods=['PUT'])
@swag_from({
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'type': {'type': 'string'},
                    'description': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Componente actualizado'},
        400: {'description': 'Error de validación'},
        404: {'description': 'No encontrado'}
    }
})
def update_component(id):
    data = request.get_json()
    return controller.update_component(id, data)

@bp.route('/components/<int:id>', methods=['DELETE'])
@swag_from({
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        204: {'description': 'Componente eliminado'},
        404: {'description': 'No encontrado'}
    }
})
def delete_component(id):
    return controller.delete_component(id)
