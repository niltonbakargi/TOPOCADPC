from typing import List
from models.ponto import Ponto
from utils.sigla_table import resolver

# Cores ACI do AutoCAD por índice de grupo
_CORES_GRUPOS = [1, 2, 3, 4, 5, 6, 30, 40, 50, 60, 70, 80, 90, 100, 140, 170]


def exportar_dxf(pontos: List[Ponto], caminho: str, modo: str = 'topografia') -> None:
    """
    Exporta pontos para DXF.

    modo='topografia' : pontos de estação total (múltiplos layers por descrição)
    modo='perimetro'  : perímetro topográfico (polilinha fechada + vértices)
    """
    try:
        import ezdxf
    except ImportError:
        raise ImportError("Instale ezdxf: pip install ezdxf")

    doc = ezdxf.new('R2010')
    doc.header['$INSUNITS'] = 6   # metros
    doc.header['$MEASUREMENT'] = 1  # sistema métrico
    msp = doc.modelspace()

    if modo == 'topografia':
        _exportar_topografia(doc, msp, pontos)
    else:
        _exportar_perimetro(doc, msp, pontos)

    doc.saveas(caminho)


def _exportar_topografia(doc, msp, pontos: List[Ponto]) -> None:
    """Layer pontos_brutos + um layer por grupo de descrição."""
    import ezdxf

    # Layer base
    doc.layers.add('pontos_brutos', color=7)

    por_grupo: dict[str, List[Ponto]] = {}
    for p in pontos:
        sigla = p.descricao[:3].upper()
        por_grupo.setdefault(sigla, []).append(p)

    for i, (sigla, grupo) in enumerate(sorted(por_grupo.items())):
        nome_layer = resolver(sigla).replace(' ', '_')
        cor = _CORES_GRUPOS[i % len(_CORES_GRUPOS)]
        if nome_layer not in doc.layers:
            doc.layers.add(nome_layer, color=cor)

        for p in grupo:
            msp.add_point(
                (p.x, p.y, p.cota),
                dxfattribs={'layer': nome_layer},
            )
            msp.add_text(
                f"{p.id}\n{p.cota:.3f}",
                dxfattribs={
                    'layer': nome_layer,
                    'height': 0.3,
                    'insert': (p.x, p.y),
                },
            )

    # Pontos brutos (todos)
    for p in pontos:
        msp.add_point(
            (p.x, p.y, p.cota),
            dxfattribs={'layer': 'pontos_brutos'},
        )


def _exportar_perimetro(doc, msp, pontos: List[Ponto]) -> None:
    """Polilinha fechada + vértices com rótulos."""
    doc.layers.add('PERIMETRO', color=2)
    doc.layers.add('VERTICES', color=3)
    doc.layers.add('LABELS', color=7)

    # Polilinha fechada
    coords_2d = [(p.x, p.y) for p in pontos]
    msp.add_lwpolyline(
        coords_2d,
        dxfattribs={'layer': 'PERIMETRO', 'closed': True, 'lineweight': 50},
    )

    # Vértices e rótulos
    for p in pontos:
        msp.add_point((p.x, p.y, p.cota), dxfattribs={'layer': 'VERTICES'})
        msp.add_text(
            p.id,
            dxfattribs={
                'layer': 'LABELS',
                'height': 0.5,
                'insert': (p.x, p.y),
            },
        )
