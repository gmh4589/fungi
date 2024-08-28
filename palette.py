
import numpy
from random import randint
from PyQt6.QtCore import QRect, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette
from PyQt6.QtWidgets import QDialog, QWidget, QPushButton, QSpinBox, QLabel, QLineEdit, QComboBox, QGridLayout, \
    QVBoxLayout, QHBoxLayout, QFileDialog


class PaletteSelector(QDialog):

    def __init__(self):
        super().__init__()
        self.resize(490, 350)
        self.palette_file = ''
        self.setWindowTitle("Palette Selector")
        self.setWindowIcon(QIcon('./data/fungi.ico'))
        self.centralwidget = QWidget(self)
        self.font = QFont()
        self.font.setPointSize(8)

        self.select_btn = QPushButton(self.centralwidget)
        self.select_btn.setText('Open Palette')
        self.select_btn.clicked.connect(self.open_palette)

        self.color_count_lbl = QLabel(self.centralwidget)
        self.color_count_lbl.setText('Color count:')

        self.color_count = ProgressiveSpinBox(self.centralwidget)
        self.color_count.valueChanged.connect(self.show_palette)

        self.pal_offset_lbl = QLabel(self.centralwidget)
        self.pal_offset_lbl.setText('Palette offset:')

        self.pal_offset = QSpinBox(self.centralwidget)
        self.pal_offset.setMinimum(0)
        self.pal_offset.setSingleStep(1)
        self.pal_offset.valueChanged.connect(self.show_palette)

        self.color_mode_lbl = QLabel(self.centralwidget)
        self.color_mode_lbl.setText('Color mode:')

        self.color_mode = QComboBox(self.centralwidget)
        self.color_mode.addItems(['RGB', 'RBG', 'GBR', 'GRB', 'BRG', 'BGR'])
        self.color_mode.currentIndexChanged.connect(self.show_palette)

        self.action_lbl = QLabel(self.centralwidget)
        self.action_lbl.setText('Actions with colors:')

        self.actions_value = QLineEdit(self.centralwidget)
        self.actions_value.textChanged.connect(self.show_palette)

        self.ok_btn = QPushButton(self.centralwidget)
        self.ok_btn.setText('OK')

        self.cancel_btn = QPushButton(self.centralwidget)
        self.cancel_btn.setText('CANCEL')

        positions = [x for x in range(10, 500, 30)]
        gui_elements = [self.select_btn, self.color_count_lbl, self.color_count, self.pal_offset_lbl, self.pal_offset,
                        self.color_mode_lbl, self.color_mode, self.action_lbl, self.actions_value, self.ok_btn,
                        self.cancel_btn]

        for i, widget in enumerate(gui_elements):
            widget.setGeometry(QRect(10, positions[i], 120, 25))

        self.hbox_layout = QHBoxLayout()
        self.vbox_layout = QVBoxLayout()
        self.vbox_layout.addWidget(self.select_btn)
        self.vbox_layout.addWidget(self.color_count_lbl)
        self.vbox_layout.addWidget(self.color_count)
        self.vbox_layout.addWidget(self.pal_offset_lbl)
        self.vbox_layout.addWidget(self.pal_offset)
        self.vbox_layout.addWidget(self.color_mode_lbl)
        self.vbox_layout.addWidget(self.color_mode)
        self.vbox_layout.addWidget(self.action_lbl)
        self.vbox_layout.addWidget(self.actions_value)
        self.vbox_layout.addWidget(self.ok_btn)
        self.vbox_layout.addWidget(self.cancel_btn)

        self.grid_layout = QGridLayout()
        self.hbox_layout.addLayout(self.vbox_layout)
        self.hbox_layout.addLayout(self.grid_layout)
        self.centralwidget.setLayout(self.hbox_layout)

        rows = columns = 16
        self.grid_layout.cellRect(rows, columns)

        for i in range(rows):

            for j in range(columns):
                color = QColor(randint(0, 255), randint(0, 255), randint(0, 255))
                square = ColorSquare(color)
                self.grid_layout.addWidget(square, i, j)

    def open_palette(self):
        self.palette_file = QFileDialog.getOpenFileName(self, 'Open File')[0]
        self.show_palette()

    def show_palette(self):

        if self.palette_file:

            with open(self.palette_file, 'rb') as pf:
                pf.seek(int(self.pal_offset.value()))
                color_seq = sum([[int.from_bytes(pf.read(1)) for _ in range(3)]
                                 for _ in range(int(self.color_count.text()))], [])

            color_count = int(self.color_count.text())
            rows, columns = (int(numpy.sqrt(color_count)),
                             int(numpy.sqrt(color_count))) if color_count > 255 else (16, 16)

            for i in reversed(range(self.grid_layout.count())):
                self.grid_layout.itemAt(i).widget().deleteLater()

            self.grid_layout.cellRect(rows, columns)
            color_num = 0

            for i in range(rows):

                for j in range(columns):

                    try:
                        r = color_seq[color_num + self.color_mode.currentText().index('R')]
                        g = color_seq[color_num + self.color_mode.currentText().index('G')]
                        b = color_seq[color_num + self.color_mode.currentText().index('B')]
                    except IndexError:
                        r = g = b = 255

                    if self.actions_value.text():

                        try:
                            r = eval(f"{r}{self.actions_value.text()}")
                            g = eval(f"{g}{self.actions_value.text()}")
                            b = eval(f"{b}{self.actions_value.text()}")
                        except SyntaxError:
                            pass

                    color = QColor(r, g, b)
                    square = ColorSquare(color)
                    self.grid_layout.addWidget(square, i, j)
                    color_num += 3


class ProgressiveSpinBox(QSpinBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(2, 2048)
        self.setValue(256)

    def stepBy(self, steps: int):
        current_value = self.value()

        if steps > 0:
            next_value = current_value * 2
        else:
            next_value = current_value // 2

        self.setValue(next_value)


class ColorSquare(QWidget):

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(QSize(15, 15))

    def paintEvent(self, event):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, self.color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)
