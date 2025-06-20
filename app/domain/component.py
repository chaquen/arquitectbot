from typing import List, Dict, Any

class Component:
    """Entidad de dominio para un componente de arquitectura de despliegue."""
    def __init__(
        self,
        nombre: str,
        descripcion: str,
        tipo: str,
        tecnologia: str,
        artefacto: str,
        nodo_despliegue: str,
        dependencias: List[str],
        interfaces_comunicacion: List[Dict[str, Any]],
        seguridad: List[str],
        escalabilidad: str,
        observabilidad: str,
        notas_adicionales: str,
        id: str = None
    ):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo = tipo
        self.tecnologia = tecnologia
        self.artefacto = artefacto
        self.nodo_despliegue = nodo_despliegue
        self.dependencias = dependencias
        self.interfaces_comunicacion = interfaces_comunicacion
        self.seguridad = seguridad
        self.escalabilidad = escalabilidad
        self.observabilidad = observabilidad
        self.notas_adicionales = notas_adicionales

    def to_dict(self) -> dict:
        return self.__dict__

    @staticmethod
    def from_dict(data: dict) -> 'Component':
        return Component(
            id=data.get('id'),
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            tipo=data['tipo'],
            tecnologia=data.get('tecnologia', ''),
            artefacto=data.get('artefacto', ''),
            nodo_despliegue=data.get('nodo_despliegue', ''),
            dependencias=data.get('dependencias', []),
            interfaces_comunicacion=data.get('interfaces_comunicacion', []),
            seguridad=data.get('seguridad', []),
            escalabilidad=data.get('escalabilidad', ''),
            observabilidad=data.get('observabilidad', ''),
            notas_adicionales=data.get('notas_adicionales', '')
        )
