from typing import Optional

class InterfazComunicacion:
    """Entidad de dominio para una interfaz de comunicación de un componente."""
    def __init__(
        self,
        tipo: str,
        protocolo: str,
        endpoint: str,
        puerto: int,
        descripcion: str,
        id: Optional[str] = None
    ):
        self.id = id
        self.tipo = tipo
        self.protocolo = protocolo
        self.endpoint = endpoint
        self.puerto = puerto
        self.descripcion = descripcion

    def to_dict(self) -> dict:
        return self.__dict__

    @staticmethod
    def from_dict(data: dict) -> 'InterfazComunicacion':
        return InterfazComunicacion(
            id=data.get('id'),
            tipo=data['tipo'],
            protocolo=data['protocolo'],
            endpoint=data['endpoint'],
            puerto=data['puerto'],
            descripcion=data['descripcion']
        )
