from typing import Any, Dict, List, Optional, TypedDict


class NodeSpec(TypedDict):
    label: str
    key: str
    value: Any


class RelationshipSpec(TypedDict, total=False):
    from_: NodeSpec
    to: NodeSpec
    type: str
    props: Dict[str, Any]


class GraphModel(TypedDict):
    atributos: List[Dict[str, Any]]
    componentes: List[Dict[str, Any]]
    hosts: List[Dict[str, Any]]
    metricas: List[Dict[str, Any]]
    relaciones: List[Dict[str, Any]]


CANON_LABELS = {
    "Componente": "Component",
    "Host": "Host",
    "Métrica": "Metric",
    "Metrica": "Metric",
    "Atributo": "Attribute",
}


def canonical_label(label: str) -> str:
    return CANON_LABELS.get(label, label)
