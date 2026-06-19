from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QAbstractItemView, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from models.ponto import Ponto


COLUNAS = ['ID', 'X (Este)', 'Y (Norte)', 'Cota', 'Descrição']
COR_HEADER = '#2c3e50'
COR_ALT = '#f8f9fa'


class PontosTable(QWidget):
    pontos_alterados = pyqtSignal(list)  # emite List[Ponto] ao mudar

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bloqueado = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Label
        titulo = QLabel('Vértices')
        titulo.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        layout.addWidget(titulo)

        # Tabela
        self.tabela = QTableWidget(0, len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid #dee2e6;
                border-radius: 4px;
                gridline-color: #dee2e6;
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {COR_HEADER};
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }}
            QTableWidget::item:alternate {{
                background-color: {COR_ALT};
            }}
            QTableWidget::item:selected {{
                background-color: #3498db;
                color: white;
            }}
        """)
        self.tabela.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.tabela)

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton('+ Linha')
        self.btn_del = QPushButton('− Remover')
        self.btn_up = QPushButton('↑')
        self.btn_down = QPushButton('↓')

        for btn in (self.btn_add, self.btn_del, self.btn_up, self.btn_down):
            btn.setFixedHeight(28)
            btn_layout.addWidget(btn)

        self.btn_add.clicked.connect(self._adicionar_linha)
        self.btn_del.clicked.connect(self._remover_linha)
        self.btn_up.clicked.connect(lambda: self._mover(-1))
        self.btn_down.clicked.connect(lambda: self._mover(1))

        layout.addLayout(btn_layout)

        # Contador
        self.label_count = QLabel('0 pontos')
        self.label_count.setStyleSheet('color: #6c757d; font-size: 11px;')
        layout.addWidget(self.label_count)

    # ── API pública ────────────────────────────────────────────────────────────

    def carregar_pontos(self, pontos: list):
        self._bloqueado = True
        self.tabela.setRowCount(0)
        for p in pontos:
            self._inserir_ponto(p)
        self._bloqueado = False
        self._atualizar_contador()
        self.pontos_alterados.emit(self.obter_pontos())

    def obter_pontos(self) -> list:
        pontos = []
        for row in range(self.tabela.rowCount()):
            try:
                id_ = self._cell(row, 0)
                x = float(self._cell(row, 1).replace(',', '.'))
                y = float(self._cell(row, 2).replace(',', '.'))
                cota = float(self._cell(row, 3).replace(',', '.') or '0')
                desc = self._cell(row, 4)
                pontos.append(Ponto(id=id_, x=x, y=y, cota=cota, descricao=desc))
            except (ValueError, AttributeError):
                continue
        return pontos

    def limpar(self):
        self._bloqueado = True
        self.tabela.setRowCount(0)
        self._bloqueado = False
        self._atualizar_contador()

    # ── Privados ───────────────────────────────────────────────────────────────

    def _inserir_ponto(self, p: Ponto, row: int = None):
        if row is None:
            row = self.tabela.rowCount()
        self.tabela.insertRow(row)
        valores = [p.id, f'{p.x:.3f}', f'{p.y:.3f}', f'{p.cota:.3f}', p.descricao]
        for col, val in enumerate(valores):
            item = QTableWidgetItem(val)
            if col in (1, 2, 3):
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
            self.tabela.setItem(row, col, item)

    def _adicionar_linha(self):
        row = self.tabela.rowCount()
        self.tabela.insertRow(row)
        self.tabela.setItem(row, 0, QTableWidgetItem(f'P-{row+1:02d}'))
        for col in range(1, 5):
            self.tabela.setItem(row, col, QTableWidgetItem('0'))
        self._atualizar_contador()

    def _remover_linha(self):
        rows = sorted(set(i.row() for i in self.tabela.selectedItems()), reverse=True)
        if not rows:
            return
        for row in rows:
            self.tabela.removeRow(row)
        self._atualizar_contador()
        self.pontos_alterados.emit(self.obter_pontos())

    def _mover(self, direcao: int):
        row = self.tabela.currentRow()
        destino = row + direcao
        if row < 0 or destino < 0 or destino >= self.tabela.rowCount():
            return
        for col in range(self.tabela.columnCount()):
            item_a = self.tabela.takeItem(row, col)
            item_b = self.tabela.takeItem(destino, col)
            self.tabela.setItem(row, col, item_b)
            self.tabela.setItem(destino, col, item_a)
        self.tabela.setCurrentCell(destino, self.tabela.currentColumn())
        self.pontos_alterados.emit(self.obter_pontos())

    def _cell(self, row: int, col: int) -> str:
        item = self.tabela.item(row, col)
        return item.text() if item else ''

    def _on_item_changed(self, item):
        if self._bloqueado:
            return
        self._atualizar_contador()
        self.pontos_alterados.emit(self.obter_pontos())

    def _atualizar_contador(self):
        n = self.tabela.rowCount()
        self.label_count.setText(f'{n} ponto{"s" if n != 1 else ""}')
