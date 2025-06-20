from neo4j import GraphDatabase
from app.domain.component import Component
from typing import List, Optional
import os

class Neo4jComponentRepository:
    """Repositorio para componentes usando Neo4j como backend."""
    def __init__(self):
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "test")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create(self, component: Component) -> Component:
        with self.driver.session() as session:
            result = session.write_transaction(self._create_component, component)
            return result

    @staticmethod
    def _create_component(tx, component: Component) -> Component:
        query = """
        CREATE (c:Component $props)
        SET c.id = randomUUID()
        RETURN c
        """
        props = component.to_dict()
        props.pop('id', None)
        record = tx.run(query, props=props).single()
        node = record["c"]
        props = dict(node)
        props['id'] = node['id']
        return Component.from_dict(props)

    def get_all(self) -> List[Component]:
        with self.driver.session() as session:
            return session.read_transaction(self._get_all_components)

    @staticmethod
    def _get_all_components(tx) -> List[Component]:
        query = "MATCH (c:Component) RETURN c"
        result = tx.run(query)
        return [Component.from_dict(dict(record['c'])) for record in result]

    def get_by_id(self, component_id: str) -> Optional[Component]:
        with self.driver.session() as session:
            return session.read_transaction(self._get_component_by_id, component_id)

    @staticmethod
    def _get_component_by_id(tx, component_id: str) -> Optional[Component]:
        query = "MATCH (c:Component {id: $id}) RETURN c"
        result = tx.run(query, id=component_id).single()
        if result:
            return Component.from_dict(dict(result['c']))
        return None

    def update(self, component_id: str, data: dict) -> Optional[Component]:
        with self.driver.session() as session:
            return session.write_transaction(self._update_component, component_id, data)

    @staticmethod
    def _update_component(tx, component_id: str, data: dict) -> Optional[Component]:
        query = """
        MATCH (c:Component {id: $id})
        SET c += $props
        RETURN c
        """
        data.pop('id', None)
        result = tx.run(query, id=component_id, props=data).single()
        if result:
            return Component.from_dict(dict(result['c']))
        return None

    def delete(self, component_id: str) -> bool:
        with self.driver.session() as session:
            return session.write_transaction(self._delete_component, component_id)

    @staticmethod
    def _delete_component(tx, component_id: str) -> bool:
        query = "MATCH (c:Component {id: $id}) DETACH DELETE c RETURN COUNT(c) as deleted"
        result = tx.run(query, id=component_id).single()
        return result and result['deleted'] > 0
