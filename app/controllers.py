from flask import jsonify
from app.models import Component
from app.services import ComponentService
from marshmallow import ValidationError

class ComponentController:
    def __init__(self):
        self.service = ComponentService()

    def get_all_components(self):
        components = self.service.get_all()
        return jsonify([comp.to_dict() for comp in components])

    def create_component(self, data):
        try:
            component = self.service.create(data)
            return jsonify(component.to_dict()), 201
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

    def get_component(self, id):
        component = self.service.get_by_id(id)
        if component is None:
            return jsonify({"error": "Component not found"}), 404
        return jsonify(component.to_dict())

    def update_component(self, id, data):
        try:
            component = self.service.update(id, data)
            if component is None:
                return jsonify({"error": "Component not found"}), 404
            return jsonify(component.to_dict())
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

    def delete_component(self, id):
        if self.service.delete(id):
            return '', 204
        return jsonify({"error": "Component not found"}), 404
