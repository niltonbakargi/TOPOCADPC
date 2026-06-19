import math
from typing import List, Tuple
from models.ponto import Ponto


def calcular_distancia(p1: Ponto, p2: Ponto) -> float:
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)


def calcular_azimute(p1: Ponto, p2: Ponto) -> float:
    """Retorna azimute em graus decimais (0=Norte, sentido horário)."""
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    az = math.degrees(math.atan2(dx, dy))
    return az % 360


def graus_para_gms(angulo: float) -> str:
    """Converte graus decimais para formato GMS (ex: 045°32'15.23\")."""
    graus = int(angulo)
    minutos_dec = (angulo - graus) * 60
    minutos = int(minutos_dec)
    segundos = (minutos_dec - minutos) * 60
    return f"{graus:03d}°{minutos:02d}'{segundos:05.2f}\""


def azimute_para_rumo(azimute: float) -> str:
    """Converte azimute para rumo (ex: N 45°32'15\" E)."""
    if azimute <= 90:
        return f"N {graus_para_gms(azimute)} E"
    elif azimute <= 180:
        return f"S {graus_para_gms(180 - azimute)} E"
    elif azimute <= 270:
        return f"S {graus_para_gms(azimute - 180)} W"
    else:
        return f"N {graus_para_gms(360 - azimute)} W"


def calcular_area(pontos: List[Ponto]) -> float:
    """Calcula área pelo método de Gauss (fórmula do Shoelace)."""
    n = len(pontos)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pontos[i].x * pontos[j].y
        area -= pontos[j].x * pontos[i].y
    return abs(area) / 2.0


def calcular_perimetro(pontos: List[Ponto]) -> float:
    n = len(pontos)
    if n < 2:
        return 0.0
    total = 0.0
    for i in range(n):
        total += calcular_distancia(pontos[i], pontos[(i + 1) % n])
    return total


def calcular_erro_fechamento(pontos: List[Ponto]) -> Tuple[float, float]:
    """Retorna (erro linear em metros, precisão relativa 1:X)."""
    if len(pontos) < 2:
        return 0.0, 0.0
    soma_dx = sum(pontos[(i+1) % len(pontos)].x - pontos[i].x for i in range(len(pontos)))
    soma_dy = sum(pontos[(i+1) % len(pontos)].y - pontos[i].y for i in range(len(pontos)))
    erro = math.sqrt(soma_dx**2 + soma_dy**2)
    perimetro = calcular_perimetro(pontos)
    precisao = perimetro / erro if erro > 1e-9 else float('inf')
    return erro, precisao
