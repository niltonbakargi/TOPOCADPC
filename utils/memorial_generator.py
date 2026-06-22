from typing import List
from models.ponto import Ponto
from utils.geometry import (
    calcular_distancia, calcular_azimute, graus_para_gms,
    azimute_para_rumo, calcular_area, calcular_perimetro,
    calcular_erro_fechamento,
)


def _fmt_coord(valor: float) -> str:
    """Formata coordenada com separador de milhar e vírgula decimal (padrão BR)."""
    inteiro = int(valor)
    decimal = round((valor - inteiro) * 1000)
    inteiro_fmt = f"{inteiro:,}".replace(',', '.')
    return f"{inteiro_fmt},{decimal:03d}"


def gerar_memorial(
    pontos: List[Ponto],
    usar_rumo: bool = False,
    cabecalho: str = '',
    nome_imovel: str = '',
    municipio: str = '',
    uf: str = '',
) -> str:
    if len(pontos) < 3:
        return "Insira pelo menos 3 vértices para gerar o memorial descritivo."

    area = calcular_area(pontos)
    perimetro = calcular_perimetro(pontos)
    erro, precisao = calcular_erro_fechamento(pontos)
    n = len(pontos)

    linhas: List[str] = []

    # ── Cabeçalho ─────────────────────────────────────────────────────────────
    if cabecalho:
        linhas.append(cabecalho)
        linhas.append('')

    linhas.append('MEMORIAL DESCRITIVO')
    linhas.append('=' * 70)

    if nome_imovel:
        linhas.append(f'Imóvel : {nome_imovel}')
    if municipio:
        loc = f'{municipio} – {uf}' if uf else municipio
        linhas.append(f'Local   : {loc}')
    if nome_imovel or municipio:
        linhas.append('')

    # ── Descrição do perímetro ─────────────────────────────────────────────────
    p0 = pontos[0]
    segmentos: List[str] = [
        f"Inicia-se a descrição deste perímetro no vértice {p0.id}, "
        f"de coordenadas N {_fmt_coord(p0.y)} m e E {_fmt_coord(p0.x)} m"
    ]

    for i in range(n):
        p_atual = pontos[i]
        p_prox = pontos[(i + 1) % n]

        dist = calcular_distancia(p_atual, p_prox)
        az = calcular_azimute(p_atual, p_prox)

        if usar_rumo:
            direcao_str = f"rumo {azimute_para_rumo(az)}"
        else:
            direcao_str = f"azimute {graus_para_gms(az)}"

        if i < n - 1:
            destino = (
                f"o vértice {p_prox.id}, de coordenadas "
                f"N {_fmt_coord(p_prox.y)} m e E {_fmt_coord(p_prox.x)} m"
            )
        else:
            destino = f"o vértice inicial {p_prox.id}, fechando o perímetro"

        segmentos.append(
            f"deste, segue com {direcao_str} e distância de "
            f"{dist:.2f} m, até {destino}"
        )

    linhas.append(', '.join(segmentos) + '.')
    linhas.append('')

    # ── Totais ────────────────────────────────────────────────────────────────
    linhas.append('=' * 70)
    linhas.append(f"Área total    : {area:>15,.4f} m²")
    linhas.append(f"              : {area/10000:>15,.4f} ha")
    linhas.append(f"Perímetro     : {perimetro:>15.2f} m")

    if erro > 1e-9:
        if precisao == float('inf'):
            linhas.append("Erro fechamento: 0,000 m  (perímetro fechado exato)")
        else:
            linhas.append(
                f"Erro fechamento: {erro:.4f} m  "
                f"(precisão 1:{precisao:,.0f})"
            )

    return '\n'.join(linhas)
