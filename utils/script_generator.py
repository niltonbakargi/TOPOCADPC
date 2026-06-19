# Portado fielmente do ScriptGenerator.kt do app Android.
# Mantém: layers, ordem Y,X,Z, encoding Windows-1252, ajuste de cota.

from typing import List
from models.ponto import Ponto
from utils.sigla_table import resolver


def _format_linha(y: float, x: float, cota: float, label: str) -> str:
    coord = f"{y:.3f},{x:.3f},{cota:.3f}"
    cota_str = f"{cota:.3f}"
    return f"{coord}    {cota_str} - {label}\n"


def build(pontos: List[Ponto], nomes: dict[str, str] | None = None) -> str:
    """
    Gera o conteúdo do script AutoCAD (.scr).

    pontos : lista já com cotaAltura ajustada
    nomes  : mapa sigla→nome do layer (se None, usa SiglaTable)
    """
    if nomes is None:
        nomes = {}

    sb: List[str] = []

    # ── Layer pontos_brutos (todos os pontos) ──────────────────────────────────
    sb.append("-layer\nnew\npontos_brutos\nset\npontos_brutos\n\n")
    sb.append("insert pontos\n")
    primeira = True
    for p in pontos:
        linha = _format_linha(p.y, p.x, p.cota, p.descricao)
        if primeira:
            sb.append(linha)
            primeira = False
        else:
            sb.append(f"  {linha}")

    # ── Um layer por grupo de descrição (3 primeiros caracteres) ───────────────
    por_grupo: dict[str, List[Ponto]] = {}
    for p in pontos:
        sigla = p.descricao[:3].upper()
        por_grupo.setdefault(sigla, []).append(p)

    for sigla in por_grupo:  # mantém ordem de inserção (por cota, como no app mobile)
        grupo = por_grupo[sigla]
        nome_layer = (nomes.get(sigla) or resolver(sigla)).replace(' ', '_')
        sb.append(f"-layer\nnew\n{nome_layer}\nset\n{nome_layer}\n\n")
        sb.append("insert pontos\n")
        primeira_grupo = True
        for p in grupo:
            linha = _format_linha(p.y, p.x, p.cota, sigla)
            if primeira_grupo:
                sb.append(linha)
                primeira_grupo = False
            else:
                sb.append(f"  {linha}")

    return ''.join(sb)


def aplicar_ajuste(pontos: List[Ponto], cota_referencia: float, cota_desejada: float) -> List[Ponto]:
    """Aplica ajuste de cota em todos os pontos mantendo a ordem original (por cota)."""
    ajuste = cota_desejada - cota_referencia
    return [Ponto(id=p.id, x=p.x, y=p.y, cota=p.cota + ajuste, descricao=p.descricao)
            for p in pontos]


def salvar_script(conteudo: str, caminho: str) -> None:
    """Salva o script com encoding Windows-1252 (compatível com AutoCAD)."""
    with open(caminho, 'w', encoding='windows-1252', errors='replace') as f:
        f.write(conteudo)
