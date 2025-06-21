from app.domain.component import Component
from app.infrastructure.neo4j_repository import Neo4jComponentRepository
from typing import List, Optional

class ComponentService:
    """Use case for managing components."""
    def __init__(self):
        """Initializes the service with a Neo4j repository instance."""
        self.repo = Neo4jComponentRepository()

    def create_component(self, data: dict) -> Component:
        """
        Create a new component in the database.

        Args:
            data (dict): Dictionary with component properties.

        Returns:
            Component: The created component instance.
        """
        component = Component.from_dict(data)
        return self.repo.create(component)

    def get_all_components(self) -> List[Component]:
        """
        Retrieve all components from the database.

        Returns:
            List[Component]: List of all components.
        """
        return self.repo.get_all()

    def get_component(self, component_id: str) -> Optional[Component]:
        """
        Retrieve a component by its ID.

        Args:
            component_id (str): The component's unique identifier.

        Returns:
            Optional[Component]: The component if found, else None.
        """
        return self.repo.get_by_id(component_id)

    def update_component(self, component_id: str, data: dict) -> Optional[Component]:
        """
        Update an existing component by its ID.

        Args:
            component_id (str): The component's unique identifier.
            data (dict): Dictionary with updated properties.

        Returns:
            Optional[Component]: The updated component if found, else None.
        """
        return self.repo.update(component_id, data)

    def delete_component(self, component_id: str) -> bool:
        """
        Delete a component by its ID.

        Args:
            component_id (str): The component's unique identifier.

        Returns:
            bool: True if deleted, False if not found.
        """
        return self.repo.delete(component_id)

    def connect_components(self, id_from: str, id_to: str, props: dict) -> bool:
        """
        Create a relationship between two components.

        Args:
            id_from (str): ID of the source component.
            id_to (str): ID of the target component.
            props (dict): Properties for the relationship.

        Returns:
            bool: True if the connection was created, False otherwise.
        """
        return self.repo.connect_components(id_from, id_to, props)

    def close(self):
        """Closes the repository connection."""
        self.repo.close()
