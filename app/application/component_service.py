from app.domain.component import Component
from app.infrastructure.neo4j_repository import Neo4jComponentRepository
from typing import List, Optional

class ComponentService:
    """Caso de uso para la gestión de componentes."""
    def __init__(self):
        self.repo = Neo4jComponentRepository()

    def create_component(self, data: dict) -> Component:
        component = Component.from_dict(data)
        return self.repo.create(component)

    def get_all_components(self) -> List[Component]:
        return self.repo.get_all()

    def get_component(self, component_id: str) -> Optional[Component]:
        return self.repo.get_by_id(component_id)

    def update_component(self, component_id: str, data: dict) -> Optional[Component]:
        return self.repo.update(component_id, data)

    def delete_component(self, component_id: str) -> bool:
        return self.repo.delete(component_id)

    def close(self):
        self.repo.close()
