import json
import os
from glob import glob
from typing import Any, Dict, List, Tuple

from app.domain.graph_model import canonical_label
from app.infrastructure.neo4j_generic_repository import Neo4jGenericRepository


class ModelImportService:
    def __init__(self):
        self.repo = Neo4jGenericRepository()

    def close(self):
        self.repo.close()

    # ------------- Loaders -------------
    @staticmethod
    def load_from_file(path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_from_folders(model_dir: str, rel_dir: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "atributos": [],
            "componentes": [],
            "hosts": [],
            "metricas": [],
            "relaciones": [],
        }

        # Nodes
        candidate_files = [
            ("componentes", ["nodo_componentes.json", "componentes.json"]),
            ("hosts", ["nodo_host.json", "hosts.json"]),
            ("metricas", ["nodo_metricas.json", "metricas.json"]),
            ("atributos", ["nodo_atributos.json", "atributos.json"]),
        ]
        for key, names in candidate_files:
            for name in names:
                p = os.path.join(model_dir, name)
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        data[key] = json.load(f)
                    break

        # Relationships
        for rel_path in glob(os.path.join(rel_dir, "relacion_*.json")):
            with open(rel_path, "r", encoding="utf-8") as f:
                rels = json.load(f)
                if isinstance(rels, list):
                    data["relaciones"].extend(rels)

        return data

    # ------------- Importers -------------
    def ensure_constraints(self):
        self.repo.ensure_constraints()

    def import_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        stats = {
            "nodes": {"Component": 0, "Host": 0, "Metric": 0, "Attribute": 0},
            "relationships": {},
            "errors": 0,
        }

        # Nodes: Component
        for comp in data.get("componentes", []) or []:
            name = comp.get("name")
            if not name:
                stats["errors"] += 1
                continue
            props = dict(comp)
            # compat con modelo anterior
            props.setdefault("label", name)
            props.setdefault("component_type", props.get("type", ""))
            props.setdefault("id", name)
            props.setdefault("name", name)
            try:
                self.repo.merge_node("Component", "name", name, props)
                stats["nodes"]["Component"] += 1
            except Exception:
                stats["errors"] += 1

        # Nodes: Host
        for host in data.get("hosts", []) or []:
            name = host.get("name")
            if not name:
                stats["errors"] += 1
                continue
            props = dict(host)
            props.setdefault("name", name)
            try:
                self.repo.merge_node("Host", "name", name, props)
                stats["nodes"]["Host"] += 1
            except Exception:
                stats["errors"] += 1

        # Nodes: Metric
        for metric in data.get("metricas", []) or []:
            name = metric.get("name")
            if not name:
                stats["errors"] += 1
                continue
            props = dict(metric)
            props.setdefault("name", name)
            try:
                self.repo.merge_node("Metric", "name", name, props)
                stats["nodes"]["Metric"] += 1
            except Exception:
                stats["errors"] += 1

        # Nodes: Attribute
        for attr in data.get("atributos", []) or []:
            name = attr.get("name")
            if not name:
                stats["errors"] += 1
                continue
            props = dict(attr)
            props.setdefault("name", name)
            try:
                self.repo.merge_node("Attribute", "name", name, props)
                stats["nodes"]["Attribute"] += 1
            except Exception:
                stats["errors"] += 1

        # Relationships
        for rel in data.get("relaciones", []) or []:
            try:
                from_spec = rel.get("from") or rel.get("from_")
                to_spec = rel.get("to")
                rel_type = rel.get("type", "RELATES")
                props = rel.get("props", {}) or {}
                if not (from_spec and to_spec and rel_type):
                    stats["errors"] += 1
                    continue

                f_label = canonical_label(str(from_spec.get("label")))
                t_label = canonical_label(str(to_spec.get("label")))
                f_key = from_spec.get("key", "name")
                t_key = to_spec.get("key", "name")
                f_val = from_spec.get("value")
                t_val = to_spec.get("value")
                if f_val is None or t_val is None:
                    stats["errors"] += 1
                    continue

                self.repo.merge_relationship(
                    f_label, f_key, f_val,
                    t_label, t_key, t_val,
                    rel_type, props,
                )
                stats["relationships"][rel_type] = stats["relationships"].get(rel_type, 0) + 1
            except Exception:
                stats["errors"] += 1

        return stats
