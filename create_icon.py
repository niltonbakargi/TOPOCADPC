"""
Gera o ícone topocad.ico para o TopocadPC.
Execute: python create_icon.py
Requer: pip install Pillow
"""

from PIL import Image, ImageDraw, ImageFont
import math


def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size

    # Fundo arredondado azul escuro
    margin = int(s * 0.04)
    d.rounded_rectangle(
        [margin, margin, s - margin, s - margin],
        radius=int(s * 0.18),
        fill=(22, 60, 110, 255),
    )

    # Polígono de terreno (triângulo irregular estilo lote topográfico)
    pad = s * 0.14
    pts = [
        (s * 0.50, pad),               # topo centro
        (s - pad, s * 0.72),           # direita baixo
        (pad,     s * 0.72),           # esquerda baixo
    ]
    # Preenchimento semitransparente
    d.polygon(pts, fill=(52, 152, 219, 180))
    # Borda branca
    d.line(pts + [pts[0]], fill=(255, 255, 255, 255), width=max(1, int(s * 0.045)))

    # Vértices (círculos brancos)
    r = max(2, int(s * 0.065))
    for x, y in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))

    # Linha de cota / eixo horizontal no rodapé
    y_base = s * 0.72
    d.line(
        [(pad * 0.6, y_base), (s - pad * 0.6, y_base)],
        fill=(241, 196, 15, 255),
        width=max(1, int(s * 0.03)),
    )

    # Marca de nível (seta pequena + traço)
    tick_x = s * 0.50
    tick_len = s * 0.07
    lw = max(1, int(s * 0.03))
    d.line(
        [(tick_x, y_base - tick_len), (tick_x, y_base + tick_len)],
        fill=(241, 196, 15, 255),
        width=lw,
    )

    return img


def main():
    sizes = [16, 32, 48, 64, 128, 256]
    frames = [draw_icon(s) for s in sizes]

    # Salva como .ico multi-resolução
    frames[0].save(
        "topocad.ico",
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=frames[1:],
    )
    print("Ícone salvo: topocad.ico")

    # Salva também um PNG 256px para visualização
    frames[-1].save("topocad_preview.png")
    print("Preview salvo: topocad_preview.png")


if __name__ == "__main__":
    main()
