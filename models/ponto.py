from dataclasses import dataclass, field


@dataclass
class Ponto:
    id: str
    x: float        # Este (Easting)
    y: float        # Norte (Northing)
    cota: float = 0.0
    descricao: str = ''

    def __str__(self):
        return f"{self.id} (E:{self.x:.3f}, N:{self.y:.3f})"
