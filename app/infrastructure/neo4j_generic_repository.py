from typing import Any, Dict
from neo4j import GraphDatabase
import os


class Neo4jGenericRepository:
    def __init__(self):
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", os.environ.get("NEO4J_USERNAME", "neo4j"))
        password = os.environ.get("NEO4J_PASSWORD", os.environ.get("NEO4J_PASS", "test1234"))
        database = os.environ.get("NEO4J_DATABASE", "neo4j")

        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver.verify_connectivity()
        self.database = database

    def close(self):
        self.driver.close()

    def ensure_constraints(self):
        stmts = [
            "CREATE CONSTRAINT component_name IF NOT EXISTS FOR (c:Component) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT host_name IF NOT EXISTS FOR (h:Host) REQUIRE h.name IS UNIQUE",
            "CREATE CONSTRAINT metric_name IF NOT EXISTS FOR (m:Metric) REQUIRE m.name IS UNIQUE",
            "CREATE CONSTRAINT attribute_name IF NOT EXISTS FOR (a:Attribute) REQUIRE a.name IS UNIQUE",
        ]
        with self.driver.session(database=self.database) as session:
            for q in stmts:
                session.run(q)

    def merge_node(self, label: str, key: str, value: Any, props: Dict[str, Any]) -> None:
        query = f"MERGE (n:{label} {{ {key}: $value }}) SET n += $props"
        with self.driver.session(database=self.database) as session:
            session.run(query, value=value, props=props)

    def merge_relationship(
        self,
        from_label: str,
        from_key: str,
        from_value: Any,
        to_label: str,
        to_key: str,
        to_value: Any,
        rel_type: str,
        rel_props: Dict[str, Any],
    ) -> None:
        query = (
            f"MATCH (a:{from_label} {{ {from_key}: $from_value }}) "
            f"MATCH (b:{to_label} {{ {to_key}: $to_value }}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            f"SET r += $rel_props"
        )
        with self.driver.session(database=self.database) as session:
            session.run(
                query,
                from_value=from_value,
                to_value=to_value,
                rel_props=rel_props or {},
            )

    # ---------- Consultas de lectura ----------
    def fetch_nodes(self, label: str):
        """Devuelve todos los nodos de un label permitido."""
        allowed = {"Component", "Host", "Metric", "Attribute"}
        if label not in allowed:
            raise ValueError("Label no permitido")
        query = f"MATCH (n:{label}) RETURN n ORDER BY coalesce(n.name, n.label)"
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            return [r["n"] for r in result]

    def fetch_relationships(self):
        """Lista todas las relaciones con nodos origen y destino básicos."""
        query = (
            "MATCH (a)-[r]->(b) "
            "RETURN labels(a)[0] AS from_label, a.name AS from_name, "
            "type(r) AS type, labels(b)[0] AS to_label, b.name AS to_name, properties(r) AS props "
            "ORDER BY type, from_name, to_name"
        )
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            relaciones = []
            for rec in result:
                relaciones.append({
                    "from": {"label": rec["from_label"], "key": "name", "value": rec["from_name"]},
                    "type": rec["type"],
                    "to": {"label": rec["to_label"], "key": "name", "value": rec["to_name"]},
                    "props": rec["props"] or {}
                })
            return relaciones

    # ---------- CRUD genérico para nodos simples (Attribute, Host, Metric) ----------
    def _validate_label(self, label: str):
        allowed = {"Component", "Host", "Metric", "Attribute"}
        if label not in allowed:
            raise ValueError("Label no permitido")

    def get_node(self, label: str, key: str, value: Any):
        self._validate_label(label)
        if key != "name":
            raise ValueError("Solo se permite buscar por la propiedad 'name'")
        query = f"MATCH (n:{label} {{ {key}: $value }}) RETURN n"
        with self.driver.session(database=self.database) as session:
            rec = session.run(query, value=value).single()
            return dict(rec["n"]) if rec else None

    def delete_node(self, label: str, key: str, value: Any) -> bool:
        self._validate_label(label)
        if key != "name":
            raise ValueError("Solo se permite eliminar por la propiedad 'name'")
        query = f"MATCH (n:{label} {{ {key}: $value }}) DETACH DELETE n RETURN COUNT(n) AS deleted"
        with self.driver.session(database=self.database) as session:
            rec = session.run(query, value=value).single()
            return rec and rec["deleted"] > 0

    def update_node(self, label: str, key: str, value: Any, props: Dict[str, Any]):
        self._validate_label(label)
        if key != "name":
            raise ValueError("Solo se permite actualizar por la propiedad 'name'")
        # Evitar sobreescribir la key fundamental
        props = dict(props or {})
        props.pop(key, None)
        set_fragment = ", ".join([f"n.{k} = $props.{k}" for k in props.keys()]) if props else ""
        if set_fragment:
            query = f"MATCH (n:{label} {{ {key}: $value }}) SET n += $props RETURN n"
        else:
            query = f"MATCH (n:{label} {{ {key}: $value }}) RETURN n"
        with self.driver.session(database=self.database) as session:
            rec = session.run(query, value=value, props=props).single()
            return dict(rec["n"]) if rec else None
