import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QToolBar, QStatusBar, QFileDialog, QMessageBox, QLabel,
)
from PyQt6.QtGui import QAction, QIcon, QFont, QColor, QPalette
from PyQt6.QtCore import Qt, QSize

from utils.csv_processor import processar_csv
from ui.widgets.pontos_table import PontosTable
from ui.widgets.mapa_widget import MapaWidget
from ui.widgets.memorial_widget import MemorialWidget
from ui.dialogs.script_dialog import ScriptDialog


STYLE = """
QMainWindow {
    background-color: #f0f2f5;
}
QToolBar {
    background-color: #2c3e50;
    border: none;
    spacing: 4px;
    padding: 4px 8px;
}
QToolBar QToolButton {
    color: white;
    border: none;
    border-radius: 4px;
    padding: 5px 12px;
    font-size: 12px;
}
QToolBar QToolButton:hover {
    background-color: #3d5166;
}
QToolBar QToolButton:pressed {
    background-color: #1a252f;
}
QToolBar::separator {
    width: 1px;
    background: #4a6278;
    margin: 4px 6px;
}
QLabel#toolbar_title {
    color: #ecf0f1;
    font-size: 15px;
    font-weight: bold;
    padding: 0 12px;
}
QStatusBar {
    background-color: #2c3e50;
    color: #ecf0f1;
    font-size: 11px;
}
QSplitter::handle {
    background-color: #dee2e6;
    width: 3px;
}
"""

PANEL_STYLE = """
    background-color: white;
    border-radius: 6px;
    border: 1px solid #dee2e6;
"""


class PainelWidget(QWidget):
    """Painel com fundo branco e padding."""
    def __init__(self, widget: QWidget, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(widget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Topocad PC')
        self.resize(1400, 800)
        self.setStyleSheet(STYLE)
        self._build_ui()

    def _build_ui(self):
        # ── Toolbar ───────────────────────────────────────────────────────────
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        titulo = QLabel('⬡ TOPOCAD PC')
        titulo.setObjectName('toolbar_title')
        toolbar.addWidget(titulo)
        toolbar.addSeparator()

        acao_abrir = QAction('📂  Importar CSV', self)
        acao_abrir.setShortcut('Ctrl+O')
        acao_abrir.triggered.connect(self._importar_csv)
        toolbar.addAction(acao_abrir)

        acao_limpar = QAction('🗑  Limpar', self)
        acao_limpar.triggered.connect(self._limpar_tudo)
        toolbar.addAction(acao_limpar)

        toolbar.addSeparator()

        acao_gerar = QAction('📄  Gerar Memorial', self)
        acao_gerar.setShortcut('Ctrl+G')
        acao_gerar.triggered.connect(self._gerar_memorial)
        toolbar.addAction(acao_gerar)

        acao_salvar = QAction('💾  Salvar Memorial', self)
        acao_salvar.setShortcut('Ctrl+S')
        acao_salvar.triggered.connect(self._salvar_memorial)
        toolbar.addAction(acao_salvar)

        toolbar.addSeparator()

        acao_script = QAction('⚙  Script AutoCAD (.scr)', self)
        acao_script.setShortcut('Ctrl+R')
        acao_script.triggered.connect(self._abrir_script_dialog)
        toolbar.addAction(acao_script)

        acao_dxf = QAction('📐  Exportar DXF', self)
        acao_dxf.triggered.connect(self._exportar_dxf)
        toolbar.addAction(acao_dxf)

        # Guarda referência para o nome do arquivo importado
        self._nome_arquivo_atual = 'levantamento'

        # ── Widgets internos ──────────────────────────────────────────────────
        self.tabela = PontosTable()
        self.mapa = MapaWidget()
        self.memorial = MemorialWidget()

        self.tabela.pontos_alterados.connect(self._on_pontos_alterados)

        # ── Splitter ──────────────────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(PainelWidget(self.tabela))
        splitter.addWidget(PainelWidget(self.mapa))
        splitter.addWidget(PainelWidget(self.memorial))
        splitter.setSizes([280, 680, 380])
        splitter.setChildrenCollapsible(False)

        central = QWidget()
        central.setStyleSheet('background-color: #f0f2f5;')
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.addWidget(splitter)
        self.setCentralWidget(central)

        # ── Status bar ────────────────────────────────────────────────────────
        self._lbl_status = QLabel('Pronto')
        self._lbl_area = QLabel('')
        self._lbl_perim = QLabel('')

        sb = self.statusBar()
        sb.addWidget(self._lbl_status, 1)
        sb.addPermanentWidget(self._lbl_area)
        sb.addPermanentWidget(QLabel('  |  '))
        sb.addPermanentWidget(self._lbl_perim)

    # ── Slots ──────────────────────────────────────────────────────────────────

    def _importar_csv(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, 'Importar CSV de Levantamento',
            os.path.expanduser('~/Downloads'),
            'Arquivos CSV (*.csv *.txt);;Todos os arquivos (*)',
        )
        if not caminho:
            return

        pontos, erro = processar_csv(caminho)
        if not pontos:
            QMessageBox.warning(self, 'Erro ao importar', erro or 'Arquivo inválido.')
            return

        self.tabela.carregar_pontos(pontos)
        nome = os.path.basename(caminho)
        self._nome_arquivo_atual = os.path.splitext(nome)[0]
        self._lbl_status.setText(f'{len(pontos)} pontos carregados de "{nome}"')

        if erro:  # aviso (linhas ignoradas)
            self.statusBar().showMessage(f'Aviso: {erro}', 4000)

    def _on_pontos_alterados(self, pontos: list):
        self.mapa.atualizar(pontos)
        self.memorial.atualizar_pontos(pontos)
        self._atualizar_status(pontos)

    def _atualizar_status(self, pontos: list):
        from utils.geometry import calcular_area, calcular_perimetro
        if len(pontos) >= 3:
            area = calcular_area(pontos)
            perim = calcular_perimetro(pontos)
            self._lbl_area.setText(f'Área: {area:,.2f} m²')
            self._lbl_perim.setText(f'Perímetro: {perim:.2f} m')
        else:
            self._lbl_area.setText('')
            self._lbl_perim.setText('')

    def _gerar_memorial(self):
        self.memorial.gerar()

    def _salvar_memorial(self):
        texto = self.memorial.texto.toPlainText()
        if not texto.strip():
            QMessageBox.information(self, 'Aviso', 'Gere o memorial antes de salvar.')
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self, 'Salvar Memorial Descritivo',
            os.path.expanduser('~/Desktop/memorial_descritivo.txt'),
            'Arquivo de Texto (*.txt);;Todos os arquivos (*)',
        )
        if not caminho:
            return

        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(texto)

        self.statusBar().showMessage(f'Salvo em: {caminho}', 4000)

    def _abrir_script_dialog(self):
        pontos = self.tabela.obter_pontos()
        if not pontos:
            QMessageBox.information(self, 'Aviso', 'Importe um CSV ou adicione pontos primeiro.')
            return
        dlg = ScriptDialog(pontos, nome_arquivo=self._nome_arquivo_atual, parent=self)
        dlg.exec()

    def _exportar_dxf(self):
        pontos = self.tabela.obter_pontos()
        if not pontos:
            QMessageBox.information(self, 'Aviso', 'Importe um CSV ou adicione pontos primeiro.')
            return

        # Detecta modo automaticamente: muitas descrições distintas = topografia
        descricoes = {p.descricao[:3].upper() for p in pontos}
        modo = 'topografia' if len(descricoes) > 2 else 'perimetro'

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            'Exportar DXF',
            os.path.expanduser(f'~/Desktop/{self._nome_arquivo_atual}.dxf'),
            'Arquivo DXF (*.dxf);;Todos os arquivos (*)',
        )
        if not caminho:
            return

        try:
            from utils.dxf_exporter import exportar_dxf
            exportar_dxf(pontos, caminho, modo=modo)
            self.statusBar().showMessage(f'DXF salvo em: {caminho}', 5000)
        except ImportError:
            QMessageBox.warning(
                self, 'Dependência ausente',
                'Instale ezdxf:\n\npip install ezdxf',
            )
        except Exception as e:
            QMessageBox.critical(self, 'Erro ao exportar DXF', str(e))

    def _limpar_tudo(self):
        resp = QMessageBox.question(
            self, 'Limpar', 'Deseja limpar todos os dados?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.tabela.limpar()
            self.mapa.limpar()
            self.memorial.limpar()
            self._lbl_status.setText('Pronto')
            self._lbl_area.setText('')
            self._lbl_perim.setText('')
