from typing import List, Dict, Any

class Component:
    """
    Domain entity for a deployment architecture component.
    Represents a system component with its main properties.
    """
    def __init__(
        self,
        id: str = None,
        label: str = '',
        component_type: str = '',
        type: str = '',
        location: str = '',
        technology: str = '',
        host: str = '',
        description: str = '',
        interface: str = ''
    ):
        """
        Initialize a Component instance.
        Args:
            id (str, optional): Unique identifier.
            label (str): Display label for the component.
            component_type (str): Type of the component (e.g., Service, Database).
            type (str): Subtype or further classification.
            location (str): Physical or logical location.
            technology (str): Technology stack used.
            host (str): Hostname or address.
            description (str): Description of the component.
            interface (str): Main interface type (e.g., REST, gRPC).
        """
        self.id = id
        self.label = label
        self.component_type = component_type
        self.type = type
        self.location = location
        self.technology = technology
        self.host = host
        self.description = description
        self.interface = interface

    def to_dict(self) -> dict:
        """
        Serialize the component to a dictionary.
        Returns:
            dict: Dictionary representation of the component.
        """
        return {
            'id': self.id,
            'label': self.label,
            'component_type': self.component_type,
            'type': self.type,
            'location': self.location,
            'technology': self.technology,
            'host': self.host,
            'description': self.description,
            'interface': self.interface
        }

    @staticmethod
    def from_dict(data: dict) -> 'Component':
        """
        Create a Component instance from a dictionary.
        Args:
            data (dict): Dictionary with component properties.
        Returns:
            Component: The created component instance.
        """
        return Component(
            id=data.get('id'),
            label=data.get('label', ''),
            component_type=data.get('component_type', ''),
            type=data.get('type', ''),
            location=data.get('location', ''),
            technology=data.get('technology', ''),
            host=data.get('host', ''),
            description=data.get('description', ''),
            interface=data.get('interface', '')
        )
