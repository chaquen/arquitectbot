from flask import Blueprint, request, jsonify
from app.application.component_service import ComponentService
from flasgger import swag_from

bp = Blueprint('component_api', __name__)
service = ComponentService()

@bp.route('/componentes', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Lista de componentes',
            'examples': {
                'application/json': [
                    {'nombre': 'auth-service', 'tipo': 'Microservicio'}
                ]
            }
        }
    }
})
def get_components():
    components = service.get_all_components()
    return jsonify([c.to_dict() for c in components]), 200

@bp.route('/componentes/<component_id>', methods=['GET'])
@swag_from({'responses': {200: {'description': 'Componente encontrado'}, 404: {'description': 'No encontrado'}}})
def get_component(component_id):
    component = service.get_component(component_id)
    if component:
        return jsonify(component.to_dict()), 200
    return jsonify({'error': 'No encontrado'}), 404

@bp.route('/componentes', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string'},
                    'descripcion': {'type': 'string'},
                    'tipo': {'type': 'string'},
                    'tecnologia': {'type': 'string'},
                    'artefacto': {'type': 'string'},
                    'nodo_despliegue': {'type': 'string'},
                    'dependencias': {'type': 'array', 'items': {'type': 'string'}},
                    'interfaces_comunicacion': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'tipo': {'type': 'string'},
                                'protocolo': {'type': 'string'},
                                'endpoint': {'type': 'string'},
                                'puerto': {'type': 'integer'},
                                'descripcion': {'type': 'string'}
                            }
                        }
                    },
                    'seguridad': {'type': 'array', 'items': {'type': 'string'}},
                    'escalabilidad': {'type': 'string'},
                    'observabilidad': {'type': 'string'},
                    'notas_adicionales': {'type': 'string'}
                },
                'required': ['nombre', 'tipo']
            }
        }
    ],
    'responses': {201: {'description': 'Creado'}, 400: {'description': 'Error de validación'}}
})
def create_component():
    data = request.get_json()
    try:
        component = service.create_component(data)
        return jsonify(component.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/componentes/<component_id>', methods=['PUT'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string'},
                    'descripcion': {'type': 'string'},
                    'tipo': {'type': 'string'},
                    'tecnologia': {'type': 'string'},
                    'artefacto': {'type': 'string'},
                    'nodo_despliegue': {'type': 'string'},
                    'dependencias': {'type': 'array', 'items': {'type': 'string'}},
                    'interfaces_comunicacion': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'tipo': {'type': 'string'},
                                'protocolo': {'type': 'string'},
                                'endpoint': {'type': 'string'},
                                'puerto': {'type': 'integer'},
                                'descripcion': {'type': 'string'}
                            }
                        }
                    },
                    'seguridad': {'type': 'array', 'items': {'type': 'string'}},
                    'escalabilidad': {'type': 'string'},
                    'observabilidad': {'type': 'string'},
                    'notas_adicionales': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {200: {'description': 'Actualizado'}, 404: {'description': 'No encontrado'}}
})
def update_component(component_id):
    data = request.get_json()
    component = service.update_component(component_id, data)
    if component:
        return jsonify(component.to_dict()), 200
    return jsonify({'error': 'No encontrado'}), 404

@bp.route('/componentes/<component_id>', methods=['DELETE'])
@swag_from({'responses': {204: {'description': 'Eliminado'}, 404: {'description': 'No encontrado'}}})
def delete_component(component_id):
    if service.delete_component(component_id):
        return '', 204
    return jsonify({'error': 'No encontrado'}), 404
