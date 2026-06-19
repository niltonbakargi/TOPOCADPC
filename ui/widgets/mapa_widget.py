import math
import numpy as np
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from models.ponto import Ponto
from utils.geometry import calcular_area, calcular_perimetro


class MapaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        titulo = QLabel('Visualização do Perímetro')
        titulo.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        layout.addWidget(titulo)

        self.figure = Figure(facecolor='#f8f9fa')
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.setStyleSheet('QToolBar { border: none; background: #f8f9fa; }')

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self._desenhar_vazio()

    # ── API pública ────────────────────────────────────────────────────────────

    def atualizar(self, pontos: list):
        self.ax.clear()
        if len(pontos) < 2:
            self._desenhar_vazio()
            return
        self._desenhar_perimetro(pontos)
        self.canvas.draw()

    def limpar(self):
        self.ax.clear()
        self._desenhar_vazio()
        self.canvas.draw()

    # ── Privados ───────────────────────────────────────────────────────────────

    def _desenhar_vazio(self):
        self.ax.set_facecolor('#ffffff')
        self.ax.text(
            0.5, 0.5, 'Importe um CSV ou\nadicione pontos na tabela',
            transform=self.ax.transAxes,
            ha='center', va='center',
            fontsize=11, color='#adb5bd',
            style='italic',
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#dee2e6')
        self.canvas.draw()

    def _desenhar_perimetro(self, pontos: list):
        xs = [p.x for p in pontos]
        ys = [p.y for p in pontos]

        # Fechar o polígono
        xs_fechado = xs + [xs[0]]
        ys_fechado = ys + [ys[0]]

        ax = self.ax
        ax.set_facecolor('#ffffff')

        # Polígono preenchido
        ax.fill(xs, ys, color='#3498db', alpha=0.12, zorder=1)

        # Contorno
        ax.plot(xs_fechado, ys_fechado,
                color='#2980b9', linewidth=2, zorder=2, solid_capstyle='round')

        # Vértices
        ax.scatter(xs, ys, s=40, color='#e74c3c', zorder=4)

        # Labels dos vértices
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        offset_fator = max(
            max(xs) - min(xs),
            max(ys) - min(ys),
        ) * 0.015

        for p in pontos:
            dx = p.x - cx
            dy = p.y - cy
            mag = math.sqrt(dx**2 + dy**2) or 1
            ox = (dx / mag) * offset_fator
            oy = (dy / mag) * offset_fator
            ax.annotate(
                p.id,
                (p.x, p.y),
                xytext=(p.x + ox, p.y + oy),
                fontsize=8,
                color='#2c3e50',
                fontweight='bold',
                ha='center', va='center',
                zorder=5,
            )

        # Seta de norte
        self._desenhar_norte(ax)

        # Barra de escala
        self._desenhar_escala(ax, xs, ys)

        # Área no centro
        area = calcular_area(pontos)
        perim = calcular_perimetro(pontos)
        ax.text(
            cx, cy,
            f'A = {area:,.2f} m²\n({area/10000:.4f} ha)\nP = {perim:.2f} m',
            ha='center', va='center',
            fontsize=8.5, color='#2c3e50',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor='#dee2e6', alpha=0.85),
            zorder=6,
        )

        ax.set_aspect('equal', adjustable='datalim')
        ax.margins(0.12)
        ax.tick_params(labelsize=8)
        ax.set_xlabel('Este (m)', fontsize=9)
        ax.set_ylabel('Norte (m)', fontsize=9)
        ax.grid(True, color='#dee2e6', linestyle='--', linewidth=0.5, alpha=0.7)

        for spine in ax.spines.values():
            spine.set_edgecolor('#dee2e6')

        self.figure.tight_layout()

    def _desenhar_norte(self, ax):
        """Seta de norte no canto superior direito (coordenadas de eixo)."""
        ax.annotate(
            'N', xy=(0.95, 0.90), xytext=(0.95, 0.80),
            xycoords='axes fraction', textcoords='axes fraction',
            ha='center', va='center',
            fontsize=10, fontweight='bold', color='#2c3e50',
            arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=2),
        )

    def _desenhar_escala(self, ax, xs, ys):
        """Barra de escala automática no canto inferior direito."""
        largura = max(xs) - min(xs)
        if largura <= 0:
            return

        # Escolhe intervalo de escala "redondo"
        alvo = largura * 0.2
        potencia = 10 ** math.floor(math.log10(alvo))
        intervalo = round(alvo / potencia) * potencia

        x_fim = min(xs) + largura * 0.95
        x_ini = x_fim - intervalo
        y_bar = min(ys) - (max(ys) - min(ys)) * 0.06

        ax.plot([x_ini, x_fim], [y_bar, y_bar], 'k-', lw=3, zorder=5)
        ax.text(
            (x_ini + x_fim) / 2, y_bar,
            f'{intervalo:.0f} m',
            ha='center', va='top',
            fontsize=8, color='#2c3e50',
            zorder=5,
        )
