from app import db
from app.models import Component
from marshmallow import Schema, fields, ValidationError

class ComponentSchema(Schema):
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    description = fields.Str()

class ComponentService:
    def __init__(self):
        self.schema = ComponentSchema()

    def get_all(self):
        return Component.query.all()

    def get_by_id(self, id):
        return Component.query.get(id)

    def create(self, data):
        # Validate input data
        self.schema.load(data)
        
        component = Component()
        component.from_dict(data)
        
        db.session.add(component)
        db.session.commit()
        return component

    def update(self, id, data):
        # Validate input data
        self.schema.load(data)
        
        component = self.get_by_id(id)
        if component is None:
            return None
            
        component.from_dict(data)
        db.session.commit()
        return component

    def delete(self, id):
        component = self.get_by_id(id)
        if component is None:
            return False
            
        db.session.delete(component)
        db.session.commit()
        return True
