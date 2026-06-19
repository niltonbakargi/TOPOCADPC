from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QLineEdit, QGroupBox, QRadioButton, QButtonGroup,
    QApplication, QSizePolicy,
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from utils.memorial_generator import gerar_memorial


class MemorialWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pontos = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        titulo = QLabel('Memorial Descritivo')
        titulo.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        layout.addWidget(titulo)

        # ── Opções ────────────────────────────────────────────────────────────
        grupo_opts = QGroupBox('Opções')
        grupo_opts.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin-top: 6px;
                padding-top: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                color: #6c757d;
            }
        """)
        opts_layout = QVBoxLayout(grupo_opts)
        opts_layout.setSpacing(4)

        # Formato de direção
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel('Direção:'))
        self.rb_azimute = QRadioButton('Azimute')
        self.rb_rumo = QRadioButton('Rumo')
        self.rb_azimute.setChecked(True)
        self.btn_fmt = QButtonGroup()
        self.btn_fmt.addButton(self.rb_azimute)
        self.btn_fmt.addButton(self.rb_rumo)
        fmt_layout.addWidget(self.rb_azimute)
        fmt_layout.addWidget(self.rb_rumo)
        fmt_layout.addStretch()
        opts_layout.addLayout(fmt_layout)

        # Campos de texto
        for label, attr in [
            ('Imóvel:', 'edit_imovel'),
            ('Município:', 'edit_municipio'),
            ('UF:', 'edit_uf'),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            edit = QLineEdit()
            edit.setFixedHeight(24)
            edit.setStyleSheet('border: 1px solid #ced4da; border-radius: 3px; padding: 2px 4px;')
            setattr(self, attr, edit)
            row.addWidget(edit)
            opts_layout.addLayout(row)

        layout.addWidget(grupo_opts)

        # ── Botão gerar ───────────────────────────────────────────────────────
        self.btn_gerar = QPushButton('Gerar Memorial')
        self.btn_gerar.setFixedHeight(32)
        self.btn_gerar.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #3d5166; }
            QPushButton:pressed { background-color: #1a252f; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        self.btn_gerar.clicked.connect(self.gerar)
        layout.addWidget(self.btn_gerar)

        # ── Texto do memorial ─────────────────────────────────────────────────
        self.texto = QTextEdit()
        self.texto.setReadOnly(True)
        self.texto.setFont(QFont('Courier New', 9))
        self.texto.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: #ffffff;
                color: #2c3e50;
                padding: 8px;
            }
        """)
        self.texto.setPlaceholderText(
            'O memorial descritivo aparecerá aqui após clicar em "Gerar Memorial".'
        )
        layout.addWidget(self.texto)

        # ── Botões de ação ────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        self.btn_copiar = QPushButton('Copiar')
        self.btn_copiar.setFixedHeight(28)
        self.btn_copiar.clicked.connect(self._copiar)
        btn_layout.addWidget(self.btn_copiar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        for btn in (self.btn_copiar,):
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #2c3e50;
                    border-radius: 4px;
                    padding: 0 12px;
                    color: #2c3e50;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #eaf0fb; }
            """)

    # ── API pública ────────────────────────────────────────────────────────────

    def atualizar_pontos(self, pontos: list):
        self._pontos = pontos

    def gerar(self):
        if not self._pontos:
            self.texto.setPlainText('Nenhum ponto carregado.')
            return

        texto = gerar_memorial(
            self._pontos,
            usar_rumo=self.rb_rumo.isChecked(),
            nome_imovel=self.edit_imovel.text().strip(),
            municipio=self.edit_municipio.text().strip(),
            uf=self.edit_uf.text().strip(),
        )
        self.texto.setPlainText(texto)

    def limpar(self):
        self._pontos = []
        self.texto.clear()

    # ── Privados ───────────────────────────────────────────────────────────────

    def _copiar(self):
        txt = self.texto.toPlainText()
        if txt:
            QApplication.clipboard().setText(txt)
            self.btn_copiar.setText('Copiado!')
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, lambda: self.btn_copiar.setText('Copiar'))
