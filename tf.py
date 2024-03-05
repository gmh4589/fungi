import json
import locale
import os.path
import shutil

from PyQt6 import QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem


class AutoCompleteComboBox(QComboBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.filter_model = QStandardItemModel()
        self.setEditable(True)
        self.completer = QCompleter(self)
        self.setCompleter(self.completer)
        self.items = []
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        line_edit = self.lineEdit()
        line_edit.textEdited.connect(self.on_text_edited)

    def on_text_edited(self, text):
        self.filter_model.setRowCount(0)
        self.filter_model.appendRow(QStandardItem(self.lineEdit().text() + text
                                                  if text != self.lineEdit().text() else self.lineEdit().text()))

        for item in self.items:

            if self.lineEdit().text().lower() in item.lower():
                self.filter_model.appendRow(QStandardItem(item))

        self.setModel(self.filter_model)


class Ui_MainWindow:

    def __init__(self):

        if not os.path.exists('lang.json'):
            lang = locale.getdefaultlocale()[0].split('_')[0]

            if not os.path.exists(f'data/local/{lang}.json'):
                lang = 'en'

            shutil.copy(f'data/local/{lang}.json', f'lang.json')

        with open('lang.json', 'r', encoding='utf-8') as json_file:
            self.local = json.load(json_file)

        self.centralwidget = QWidget(self)
        self.formLayoutWidget = QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 20, 230, 290))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.widthLabel = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.widthLabel)
        self.widthInput = QSpinBox(self.formLayoutWidget)
        self.widthInput.setMaximum(100000)
        self.widthInput.setSingleStep(1)
        self.widthInput.setProperty("value", 512)
        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.widthInput)
        self.heightLabel = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.heightLabel)
        self.heightInput = QSpinBox(self.formLayoutWidget)
        self.heightInput.setMaximum(100000)
        self.heightInput.setSingleStep(1)
        self.heightInput.setProperty("value", 512)
        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.heightInput)
        self.offset_hexLabel = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.offset_hexLabel)
        self.offset_hexData = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.offset_hexData)
        self.offsetLabel = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.offsetLabel)
        self.offsetInput = QSpinBox(self.formLayoutWidget)
        self.offsetInput.setMaximum(2_000_000_000)
        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.offsetInput)
        self.zoomLabel = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.zoomLabel)
        self.zoomInput = QSpinBox(self.formLayoutWidget)
        self.zoomInput.setMinimum(10)
        self.zoomInput.setMaximum(1000)
        self.zoomInput.setSingleStep(10)
        self.zoomInput.setProperty("value", 100)
        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.zoomInput)
        self.compressLabel = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.compressLabel)
        self.compressInput = AutoCompleteComboBox(self.formLayoutWidget)
        self.formLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.compressInput)
        self.bppLabel = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.bppLabel)
        self.bppInput = QComboBox(self.formLayoutWidget)
        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.bppInput)
        self.colorLabel = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.colorLabel)
        self.color_schemeInput = QComboBox(self.formLayoutWidget)
        self.formLayout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.color_schemeInput)
        self.rotateLabel = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(9, QFormLayout.ItemRole.LabelRole, self.rotateLabel)
        self.rotateInput = QComboBox(self.formLayoutWidget)
        self.formLayout.setWidget(9, QFormLayout.ItemRole.FieldRole, self.rotateInput)
        self.formatData = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(10, QFormLayout.ItemRole.FieldRole, self.formatData)
        self.langLabel = QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(11, QFormLayout.ItemRole.LabelRole, self.langLabel)
        self.langInput = QComboBox(self.formLayoutWidget)
        self.formLayout.setWidget(11, QFormLayout.ItemRole.FieldRole, self.langInput)
        self.lng_list = {}

        for path, folder, lang_file in os.walk('data\\local'):

            for file in lang_file:

                with open(f'data/local/{file}', 'r', encoding='utf-8') as json_file:
                    lng = json.load(json_file)
                    self.lng_list[lng['lang']] = file

        self.langInput.addItems([key for key in self.lng_list.keys()])
        self.langInput.setCurrentText(self.local['lang'])
        self.tabWidget = QTabWidget(self.centralwidget)
        self.preView = QWidget()
        self.imageScrollArea = QScrollArea(self.preView)
        self.imageScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.imageScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.imageScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 520, 510))
        self.graphicsPreview = QLabel(self.scrollAreaWidgetContents)
        self.graphicsPreview.setGeometry(QtCore.QRect(0, 0, 520, 510))
        self.graphicsPreview.setAutoFillBackground(False)
        self.graphicsPreview.setStyleSheet("font: 20pt \"MS Shell Dlg 2\";")
        self.graphicsPreview.setText("")
        self.graphicsPreview.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.graphicsPreview.setScaledContents(False)
        self.graphicsPreview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.imageScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.tabWidget.addTab(self.preView, "")
        self.openButton = QPushButton(self.centralwidget)
        self.reOpenButton = QPushButton(self.centralwidget)
        self.reOpenButton.setStyleSheet('QPushButton {font-size: 15pt;}')
        self.reOpenButton.setToolTip(self.local["reopen"])
        self.saveButton = QPushButton(self.centralwidget)
        self.settingButton = QPushButton(self.centralwidget)
        self.settingButton.setStyleSheet('QPushButton {font-size: 15pt;}')
        self.label_info = QLabel(self.centralwidget)
        self.fname_info = QLabel(self.centralwidget)
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi(self)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "FUNGI (Find and UNpack Graphics and Images)"))
        self.widthLabel.setText(_translate("MainWindow", self.local["width"]))
        self.heightLabel.setText(_translate("MainWindow", self.local["height"]))
        self.offsetLabel.setText(_translate("MainWindow", self.local["offset"]))
        self.offset_hexLabel.setText(_translate("MainWindow", self.local["hex_offset"]))
        self.offset_hexData.setText(_translate("MainWindow", "0x0"))
        self.zoomLabel.setText(_translate("MainWindow", self.local["zoom"]))
        self.compressLabel.setText(_translate("MainWindow", self.local["zip"]))
        self.bppLabel.setText(_translate("MainWindow", self.local["bpp"]))
        self.colorLabel.setText(_translate("MainWindow", self.local["codec"]))
        self.rotateLabel.setText(_translate("MainWindow", self.local["change"]))
        self.saveButton.setText(_translate("MainWindow", self.local["save"]))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.preView), _translate("MainWindow", self.local["preview"]))
        self.openButton.setText(_translate("MainWindow", self.local["file_open"]))
        self.reOpenButton.setText(_translate("MainWindow", "⭯"))
        self.settingButton.setText(_translate("MainWindow", "⛭"))
        self.langLabel.setText(_translate("MainWindow", 'Language'))
