"""
Diálogo de geração de script AutoCAD (.scr) a partir de dados de estação total.
Reproduz o fluxo do app Android: selecionar ponto de referência → ajustar cota → gerar script.
"""
import os
from typing import List

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QTextEdit, QFileDialog, QFrame, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QSizePolicy, QStackedWidget, QAbstractItemView, QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from models.ponto import Ponto
from utils.script_generator import build, aplicar_ajuste, salvar_script
from utils.sigla_table import resolver, SIGLAS

BTN_STYLE_PRIMARY = """
QPushButton {
    background-color: #2c3e50; color: white;
    border-radius: 4px; padding: 6px 16px; font-weight: bold;
}
QPushButton:hover { background-color: #3d5166; }
QPushButton:disabled { background-color: #95a5a6; }
"""
BTN_STYLE_SECONDARY = """
QPushButton {
    border: 1px solid #2c3e50; border-radius: 4px;
    padding: 6px 16px; color: #2c3e50;
}
QPushButton:hover { background-color: #eaf0fb; }
"""


class ScriptDialog(QDialog):
    def __init__(self, pontos: List[Ponto], nome_arquivo: str = 'levantamento', parent=None):
        super().__init__(parent)
        self.setWindowTitle('Gerar Script AutoCAD (.scr)')
        self.resize(680, 520)
        self.setModal(True)

        # Estado do fluxo
        self._pontos_originais = sorted(pontos, key=lambda p: p.cota)
        self._pontos_fluxo: List[Ponto] = list(self._pontos_originais)
        self._nome_arquivo = nome_arquivo
        self._conteudo_script: str = ''

        self._build_ui()
        self._atualizar_step1()

    # ── Build UI ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Título + passo
        self._lbl_titulo = QLabel()
        self._lbl_titulo.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        layout.addWidget(self._lbl_titulo)

        self._lbl_passo = QLabel()
        self._lbl_passo.setStyleSheet('color: #6c757d; font-size: 11px;')
        layout.addWidget(self._lbl_passo)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet('color: #dee2e6;')
        layout.addWidget(sep)

        # Stacked pages
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.stack.addWidget(self._page_referencia())   # 0
        self.stack.addWidget(self._page_siglas())        # 1
        self.stack.addWidget(self._page_preview())       # 2

        # Botões de navegação
        nav = QHBoxLayout()
        self.btn_voltar = QPushButton('← Voltar')
        self.btn_voltar.setStyleSheet(BTN_STYLE_SECONDARY)
        self.btn_voltar.clicked.connect(self._voltar)

        self.btn_avancar = QPushButton('Avançar →')
        self.btn_avancar.setStyleSheet(BTN_STYLE_PRIMARY)
        self.btn_avancar.clicked.connect(self._avancar)

        self.btn_salvar = QPushButton('💾  Salvar .scr')
        self.btn_salvar.setStyleSheet(BTN_STYLE_PRIMARY)
        self.btn_salvar.clicked.connect(self._salvar)
        self.btn_salvar.setVisible(False)

        nav.addWidget(self.btn_voltar)
        nav.addStretch()
        nav.addWidget(self.btn_avancar)
        nav.addWidget(self.btn_salvar)
        layout.addLayout(nav)

    # ── Page 0: Seleção do ponto de referência ────────────────────────────────

    def _page_referencia(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        info = QLabel(
            'O app percorre os pontos do menor para o maior cota.\n'
            'Confirme quando chegar ao ponto que será usado como referência de nível.'
        )
        info.setWordWrap(True)
        info.setStyleSheet('color: #495057;')
        layout.addWidget(info)

        # Card do ponto atual
        card = QGroupBox('Ponto de menor cota atual')
        card.setStyleSheet("""
            QGroupBox { border: 1px solid #dee2e6; border-radius: 6px;
                        margin-top: 8px; font-weight: bold; }
            QGroupBox::title { left: 10px; color: #2c3e50; }
        """)
        card_layout = QVBoxLayout(card)

        self._lbl_ponto_id = QLabel()
        self._lbl_ponto_id.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        self._lbl_ponto_id.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._lbl_ponto_cota = QLabel()
        self._lbl_ponto_cota.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        self._lbl_ponto_cota.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_ponto_cota.setStyleSheet('color: #2980b9;')

        self._lbl_ponto_coord = QLabel()
        self._lbl_ponto_coord.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_ponto_coord.setStyleSheet('color: #6c757d; font-size: 11px;')

        card_layout.addWidget(self._lbl_ponto_id)
        card_layout.addWidget(self._lbl_ponto_cota)
        card_layout.addWidget(self._lbl_ponto_coord)
        layout.addWidget(card)

        # Botões de decisão
        decisao = QHBoxLayout()
        self.btn_proximo = QPushButton('Não é referência → Próximo')
        self.btn_proximo.setStyleSheet(BTN_STYLE_SECONDARY)
        self.btn_proximo.clicked.connect(self._proximo_ponto)

        self.btn_usar = QPushButton('✓ Usar como referência')
        self.btn_usar.setStyleSheet(BTN_STYLE_PRIMARY)
        self.btn_usar.clicked.connect(self._usar_como_referencia)

        decisao.addWidget(self.btn_proximo)
        decisao.addWidget(self.btn_usar)
        layout.addLayout(decisao)

        # Cota desejada (aparece após confirmar referência)
        self._grp_cota = QGroupBox('Cota de referência desejada')
        self._grp_cota.setStyleSheet("""
            QGroupBox { border: 1px solid #3498db; border-radius: 6px; margin-top: 8px; }
            QGroupBox::title { left: 10px; color: #2980b9; font-weight: bold; }
        """)
        self._grp_cota.setVisible(False)
        cota_layout = QHBoxLayout(self._grp_cota)

        self._lbl_referencia_escolhida = QLabel()
        self._lbl_referencia_escolhida.setStyleSheet('color: #495057;')
        cota_layout.addWidget(self._lbl_referencia_escolhida)

        cota_layout.addStretch()
        cota_layout.addWidget(QLabel('Nova cota:'))

        self.spin_cota = QDoubleSpinBox()
        self.spin_cota.setRange(-9999.999, 99999.999)
        self.spin_cota.setDecimals(3)
        self.spin_cota.setValue(0.0)
        self.spin_cota.setFixedWidth(110)
        self.spin_cota.setSuffix(' m')
        cota_layout.addWidget(self.spin_cota)

        layout.addWidget(self._grp_cota)
        layout.addStretch()

        self._cota_referencia: float | None = None
        return page

    # ── Page 1: Confirmar/renomear siglas ────────────────────────────────────

    def _page_siglas(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        info = QLabel('Verifique os nomes dos layers. Edite a coluna "Nome do Layer" se necessário.')
        info.setWordWrap(True)
        info.setStyleSheet('color: #495057;')
        layout.addWidget(info)

        self.tbl_siglas = QTableWidget(0, 2)
        self.tbl_siglas.setHorizontalHeaderLabels(['Sigla', 'Nome do Layer'])
        self.tbl_siglas.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_siglas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl_siglas.setStyleSheet("""
            QTableWidget { border: 1px solid #dee2e6; border-radius: 4px; font-size: 12px; }
            QHeaderView::section { background-color: #2c3e50; color: white;
                                   font-weight: bold; padding: 5px; border: none; }
        """)
        layout.addWidget(self.tbl_siglas)
        return page

    # ── Page 2: Preview do script ─────────────────────────────────────────────

    def _page_preview(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        self._lbl_resumo = QLabel()
        self._lbl_resumo.setStyleSheet('color: #495057; font-size: 12px;')
        layout.addWidget(self._lbl_resumo)

        self.txt_preview = QTextEdit()
        self.txt_preview.setReadOnly(True)
        self.txt_preview.setFont(QFont('Courier New', 9))
        self.txt_preview.setStyleSheet("""
            QTextEdit { border: 1px solid #dee2e6; border-radius: 4px;
                        background: #f8f9fa; color: #2c3e50; padding: 6px; }
        """)
        layout.addWidget(self.txt_preview)
        return page

    # ── Lógica do fluxo ───────────────────────────────────────────────────────

    def _atualizar_step1(self):
        self._lbl_titulo.setText('Passo 1 — Selecionar ponto de referência')
        self._lbl_passo.setText(f'Passo 1 de 3  |  {len(self._pontos_fluxo)} pontos restantes')
        self.btn_voltar.setEnabled(False)
        self.btn_avancar.setEnabled(False)

        if not self._pontos_fluxo:
            QMessageBox.warning(self, 'Aviso', 'Todos os pontos foram removidos.')
            return

        p = self._pontos_fluxo[0]
        self._lbl_ponto_id.setText(p.id)
        self._lbl_ponto_cota.setText(f'Cota: {p.cota:.3f} m')
        self._lbl_ponto_coord.setText(f'X: {p.x:.3f}   Y: {p.y:.3f}   Desc: {p.descricao}')

    def _proximo_ponto(self):
        if len(self._pontos_fluxo) <= 1:
            QMessageBox.warning(self, 'Aviso', 'Não há mais pontos para remover.')
            return
        self._pontos_fluxo.pop(0)
        self._atualizar_step1()

    def _usar_como_referencia(self):
        self._cota_referencia = self._pontos_fluxo[0].cota
        self._grp_cota.setVisible(True)
        self._lbl_referencia_escolhida.setText(
            f'Referência: {self._pontos_fluxo[0].id}  (cota original: {self._cota_referencia:.3f} m)'
        )
        self.btn_proximo.setEnabled(False)
        self.btn_usar.setEnabled(False)
        self.btn_avancar.setEnabled(True)

    def _preencher_siglas(self):
        siglas_usadas = sorted({p.descricao[:3].upper() for p in self._pontos_originais})
        self.tbl_siglas.setRowCount(0)
        for sigla in siglas_usadas:
            row = self.tbl_siglas.rowCount()
            self.tbl_siglas.insertRow(row)
            item_sigla = QTableWidgetItem(sigla)
            item_sigla.setFlags(item_sigla.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_sigla.setBackground(QColor('#f8f9fa'))
            self.tbl_siglas.setItem(row, 0, item_sigla)
            self.tbl_siglas.setItem(row, 1, QTableWidgetItem(resolver(sigla)))

    def _obter_nomes_siglas(self) -> dict:
        nomes = {}
        for row in range(self.tbl_siglas.rowCount()):
            sigla = self.tbl_siglas.item(row, 0).text()
            nome = self.tbl_siglas.item(row, 1).text().strip().replace(' ', '_')
            nomes[sigla] = nome or sigla
        return nomes

    def _gerar_script(self):
        nomes = self._obter_nomes_siglas()
        pontos_ajustados = aplicar_ajuste(
            self._pontos_originais,
            self._cota_referencia,
            self.spin_cota.value(),
        )
        self._conteudo_script = build(pontos_ajustados, nomes)

        # Resumo
        grupos = len({p.descricao[:3].upper() for p in self._pontos_originais})
        self._lbl_resumo.setText(
            f'{len(pontos_ajustados)} pontos  |  {grupos} layers de descrição  |  '
            f'Ajuste: {self.spin_cota.value() - self._cota_referencia:+.3f} m'
        )

        # Preview (primeiras 60 linhas)
        linhas = self._conteudo_script.splitlines()
        preview = '\n'.join(linhas[:60])
        if len(linhas) > 60:
            preview += f'\n... (+{len(linhas)-60} linhas)'
        self.txt_preview.setPlainText(preview)

    def _avancar(self):
        atual = self.stack.currentIndex()
        if atual == 0:
            if self._cota_referencia is None:
                QMessageBox.information(self, 'Aviso', 'Confirme o ponto de referência primeiro.')
                return
            self._preencher_siglas()
            self.stack.setCurrentIndex(1)
            self._lbl_titulo.setText('Passo 2 — Confirmar layers')
            self._lbl_passo.setText('Passo 2 de 3  |  Edite os nomes dos layers se necessário')
            self.btn_voltar.setEnabled(True)

        elif atual == 1:
            self._gerar_script()
            self.stack.setCurrentIndex(2)
            self._lbl_titulo.setText('Passo 3 — Script gerado')
            self._lbl_passo.setText('Passo 3 de 3  |  Revise e salve o arquivo .scr')
            self.btn_avancar.setVisible(False)
            self.btn_salvar.setVisible(True)

    def _voltar(self):
        atual = self.stack.currentIndex()
        if atual == 1:
            self.stack.setCurrentIndex(0)
            self._lbl_titulo.setText('Passo 1 — Selecionar ponto de referência')
            self._lbl_passo.setText(f'Passo 1 de 3  |  {len(self._pontos_fluxo)} pontos restantes')
            self.btn_voltar.setEnabled(False)
        elif atual == 2:
            self.stack.setCurrentIndex(1)
            self._lbl_titulo.setText('Passo 2 — Confirmar layers')
            self._lbl_passo.setText('Passo 2 de 3')
            self.btn_avancar.setVisible(True)
            self.btn_salvar.setVisible(False)

    def _salvar(self):
        if not self._conteudo_script:
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            'Salvar Script AutoCAD',
            os.path.expanduser(f'~/Desktop/{self._nome_arquivo}_script.scr'),
            'Script AutoCAD (*.scr);;Todos os arquivos (*)',
        )
        if not caminho:
            return

        try:
            salvar_script(self._conteudo_script, caminho)
            QMessageBox.information(
                self, 'Salvo',
                f'Script salvo em:\n{caminho}\n\n'
                f'Encoding: Windows-1252 (compatível com AutoCAD)',
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao salvar:\n{e}')
