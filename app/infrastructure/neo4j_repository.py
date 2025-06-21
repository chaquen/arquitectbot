from neo4j import GraphDatabase
from app.domain.component import Component
from typing import List, Optional
import os

class Neo4jComponentRepository:
    """Repository for components using Neo4j as backend."""
    def __init__(self):
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "test1234")
        database = os.environ.get("NEO4J_DATABASE", "neo4j")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def create(self, component: Component) -> Component:
        with self.driver.session(database=self.database) as session:
            result = session.write_transaction(self._create_component, component)
            return result

    @staticmethod
    def _create_component(tx, component: Component) -> Component:
        query = """
        CREATE (c:Component {
            label: $label,
            component_type: $component_type,
            type: $type,
            location: $location,
            technology: $technology,
            host: $host,
            description: $description,
            interface: $interface,
            id: randomUUID()
        })
        RETURN c
        """
        record = tx.run(query,
            label=component.label,
            component_type=component.component_type,
            type=component.type,
            location=component.location,
            technology=component.technology,
            host=component.host,
            description=component.description,
            interface=component.interface
        ).single()
        node = record["c"]
        return Component(
            id=node["id"],
            label=node.get("label", ""),
            component_type=node.get("component_type", ""),
            type=node.get("type", ""),
            location=node.get("location", ""),
            technology=node.get("technology", ""),
            host=node.get("host", ""),
            description=node.get("description", ""),
            interface=node.get("interface", "")
        )

    def get_by_id(self, component_id: str) -> Optional[Component]:
        with self.driver.session(database=self.database) as session:
            return session.read_transaction(self._get_component, component_id)

    @staticmethod
    def _get_component(tx, component_id: str) -> Optional[Component]:
        query = "MATCH (c:Component {id: $id}) RETURN c"
        result = tx.run(query, id=component_id).single()
        if result:
            node = result["c"]
            return Component(
                id=node["id"],
                label=node.get("label", ""),
                component_type=node.get("component_type", ""),
                type=node.get("type", ""),
                location=node.get("location", ""),
                technology=node.get("technology", ""),
                host=node.get("host", ""),
                description=node.get("description", ""),
                interface=node.get("interface", "")
            )
        return None

    def get_all(self) -> List[Component]:
        with self.driver.session(database=self.database) as session:
            return session.read_transaction(self._get_all_components)

    @staticmethod
    def _get_all_components(tx) -> List[Component]:
        query = "MATCH (c:Component) RETURN c"
        result = tx.run(query)
        return [Component(
            id=record["c"]["id"],
            label=record["c"].get("label", ""),
            component_type=record["c"].get("component_type", ""),
            type=record["c"].get("type", ""),
            location=record["c"].get("location", ""),
            technology=record["c"].get("technology", ""),
            host=record["c"].get("host", ""),
            description=record["c"].get("description", ""),
            interface=record["c"].get("interface", "")
        ) for record in result]

    def update(self, component_id: str, data: dict) -> Optional[Component]:
        with self.driver.session(database=self.database) as session:
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
            node = result["c"]
            return Component(
                id=node["id"],
                label=node.get("label", ""),
                component_type=node.get("component_type", ""),
                type=node.get("type", ""),
                location=node.get("location", ""),
                technology=node.get("technology", ""),
                host=node.get("host", ""),
                description=node.get("description", ""),
                interface=node.get("interface", "")
            )
        return None

    def delete(self, component_id: str) -> bool:
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(self._delete_component, component_id)

    @staticmethod
    def _delete_component(tx, component_id: str) -> bool:
        query = "MATCH (c:Component {id: $id}) DETACH DELETE c RETURN COUNT(c) as deleted"
        result = tx.run(query, id=component_id).single()
        return result and result['deleted'] > 0

    def connect_components(self, id_from: str, id_to: str, props: dict) -> bool:
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(self._connect_components, id_from, id_to, props)

    @staticmethod
    def _connect_components(tx, id_from: str, id_to: str, props: dict) -> bool:
        query = """
        MATCH (a:Component {id: $id_from}), (b:Component {id: $id_to})
        CREATE (a)-[r:CONNECTS_TO $props]->(b)
        RETURN r
        """
        result = tx.run(query, id_from=id_from, id_to=id_to, props=props).single()
        return result is not None
