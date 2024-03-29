import json
import os
import sys
import shutil
from subprocess import Popen, SW_HIDE

from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QRect, QTimer

from PIL import Image, ImageOps, UnidentifiedImageError, ImageFile

import converter
import codec_list
from tf import Ui_MainWindow
from zip_list import zip_methods

ImageFile.LOAD_TRUNCATED_IMAGES = True


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.resize(800, 570)
        self.file_name = ''
        self.short_name = ''
        self.ext = 'webp'
        self.temp_path = 'temp'
        # self.temp_path = os.environ['TEMP']
        self.temp_file = f'{self.temp_path}\\image.dat'

        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)

        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

        self.setWindowIcon(QIcon('data\\fungus.ico'))
        self.offsetInput.valueChanged.connect(self.dec2hex)
        self.compressInput.items = [key for key in zip_methods.keys()]
        self.compressInput.setCurrentText(self.local["no_zip"])
        self.bppInput.addItems(
            ['1BPP', '8BPP', '10BPP', '16BPP', '24BPP', '32BPP', '64BPP', '96BPP', '128BPP', 'DirectX'])
        self.bppInput.setCurrentText('32BPP')
        self.rotateInput.addItems([self.local['no'], f'90° {self.local["left"]}', f'90° {self.local["right"]}', '180°',
                                   self.local['mirror_h'], self.local['mirror_v'], self.local['invert_read'],
                                   self.local["invert"], self.local["negative"], self.local["grayscale"]])

        self.openButton.clicked.connect(self.file_open)
        self.saveButton.clicked.connect(self.save_image)
        self.reOpenButton.clicked.connect(lambda: self.file_open(reopen=True))
        self.settingButton.clicked.connect(self.hide_show_setting)

        self.widthInput.valueChanged.connect(self.draw_image)
        self.heightInput.valueChanged.connect(self.draw_image)
        self.offsetInput.valueChanged.connect(self.draw_image)
        self.zoomInput.valueChanged.connect(self.draw_image)
        self.compressInput.currentIndexChanged.connect(self.unzip)
        self.bppInput.currentIndexChanged.connect(self.createList)
        self.color_schemeInput.currentIndexChanged.connect(self.draw_image)
        self.rotateInput.currentIndexChanged.connect(self.draw_image)
        self.langInput.currentIndexChanged.connect(self.change_lang)
        self.offset_hexData.textChanged.connect(self.hex_offset_set)
        self.langInput.hide()
        self.langLabel.hide()
        self.hide_setting = True
        self.lay = QVBoxLayout(self.scrollAreaWidgetContents)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.addWidget(self.graphicsPreview)

        self.createList()
        self.color_schemeInput.setCurrentText('RGBA')
        self.imageScrollArea.setWidgetResizable(True)
        self.graphicsPreview.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.timer = QTimer(self)
        self.show()

    def hex_offset_set(self):
        hex_offset = self.offset_hexData.text()

        try:
            self.offsetInput.setValue(int(hex_offset, 16))
        except (ValueError, OverflowError):
            self.label_info.setText(f'Enter correct hex data!')

            for char in hex_offset:

                if char not in 'x0123456789abcdefABCDEF':
                    self.offset_hexData.setText(hex_offset.replace(char, ''))

    def createList(self):

        currentChange = self.bppInput.currentText()
        # bpp = str(int(int(currentChange.replace('BPP', '')) / 3))

        match currentChange:
            # 1-bit Grayscale, 2 colors palette
            case '1BPP':
                codecsList = ['1']
            case '8BPP':
                codecsList = ['L', 'A8_UNORM', 'R8_SINT', 'R8_SNORM', 'R8_UINT', 'R8_UNORM']
            case '10BPP':
                codecsList = ['Y210', 'Y410']
            # 5-bit RGB with 1-bit alpha chanel, R5G6B5, 16-bit Grayscale
            case '16BPP':
                codecsList = ['B4G4R4A4_UNORM', 'B5G5R5A1_UNORM', 'B5G6R5_UNORM',
                              'R8G8_SINT', 'R8G8_SNORM', 'R8G8_UINT', 'R8G8_UNORM',
                              'R16_FLOAT', 'R16_SINT', 'R16_SNORM', 'R16_UINT', 'R16_UNORM',
                              'LA', 'PA', 'I;16L', 'I;16B', 'Y216', 'Y416']
            # 8-bit RGB, HSL, HSV, LAB, YCbCr
            case '24BPP':
                codecsList = ['RGB', 'RBG', 'GBR', 'GRB', 'BRG', 'BGR', 'HSV', 'HSL', 'YCbCr', 'LAB', 'YUY2']
            # 8-bit RGBA, CMYK, 32-bit Grayscale
            case '32BPP':
                codecsList = ['RGBA', 'RBGA', 'GBRA', 'GRBA', 'BRGA', 'BGRA',
                              'ARGB', 'ARBG', 'AGBR', 'AGRB', 'ABRG', 'ABGR',
                              'XBGR', 'XRGB', 'BGRX', 'RGBX', 'RGBa', 'CMYK',
                              'B8G8R8A8_UNORM', 'B8G8R8A8_UNORM_SRGB', 'B8G8R8X8_UNORM', 'B8G8R8X8_UNORM_SRGB',
                              'G8R8_G8B8_UNORM', 'R10G10B10A2_UINT', 'R10G10B10A2_UNORM', 'R10G10B10_XR_BIAS_A2_UNORM',
                              'R11G11B10_FLOAT', 'R16G16_FLOAT', 'R16G16_SINT', 'R16G16_SNORM', 'R16G16_UINT',
                              'R16G16_UNORM', 'R32_FLOAT', 'R32_SINT', 'R32_UINT', 'R8G8B8A8_SINT', 'R8G8B8A8_SNORM',
                              'R8G8B8A8_UINT', 'R8G8B8A8_UNORM', 'R8G8B8A8_UNORM_SRGB', 'R8G8_B8G8_UNORM',
                              'R9G9B9E5_SHAREDEXP', 'I', 'F', 'AYUV']
            case '64BPP':
                codecsList = ['R16G16B16A16_FLOAT', 'R16G16B16A16_SINT', 'R16G16B16A16_SNORM', 'R16G16B16A16_UINT',
                              'R16G16B16A16_UNORM', 'R32G32_FLOAT', 'R32G32_SINT', 'R32G32_UINT']
            case '96BPP':
                codecsList = ['R32G32B32_FLOAT', 'R32G32B32_SINT', 'R32G32B32_UINT']
            case '128BPP':
                codecsList = ['R32G32B32A32_FLOAT', 'R32G32B32A32_SINT', 'R32G32B32A32_UINT']
            case 'DirectX':
                codecsList = ['BC1_UNORM', 'BC1_UNORM_SRGB', 'BC2_UNORM', 'BC2_UNORM_SRGB', 'BC3_UNORM',
                              'BC3_UNORM_SRGB', 'BC4_SNORM', 'BC4_UNORM', 'BC5_SNORM', 'BC5_UNORM', 'BC6H_SF16',
                              'BC6H_UF16', 'BC7_UNORM', 'BC7_UNORM_SRGB']
            case _:
                codecsList = []

        self.color_schemeInput.clear()
        self.color_schemeInput.addItems(codecsList)

    def draw_image(self):
        self.label_info.setText('')

        offset = int(self.offsetInput.value())
        width = int(self.widthInput.value())
        height = int(self.heightInput.value())
        zoom = int(self.zoomInput.value()) / 100
        rotate = self.rotateInput.currentText()

        try:

            with open(self.temp_file, 'rb') as temp_image:
                temp_image.seek(offset)
                image_data = temp_image.read()

        except FileNotFoundError:
            self.fname_info.setText(self.local["file_not_select"])
            shutil.copy('data\\fungus.png', self.temp_file)

            with open(self.temp_file, 'rb') as temp_image:
                image_data = temp_image.read()

        if rotate in (self.local["invert_read"], self.local["invert"]):
            byte_array = list(image_data)
            image_data = bytes(reversed(byte_array))

        if os.path.exists(f'{self.temp_path}\\temp.{self.ext}'):
            os.remove(f'{self.temp_path}\\temp.{self.ext}')

        codec, image_data = self.colorWrapper(image_data)

        try:
            data = Image.open(self.temp_file)
            data.save(f'{self.temp_path}\\temp.png')

            with open(self.temp_file, 'wb') as nd:
                nd.write(data.tobytes())

            w, h = data.size
            bpp = int(len(data.tobytes()) / (w * h)) * 8

            self.widthInput.setValue(w)
            self.heightInput.setValue(h)
            self.bppInput.setCurrentText(f'{bpp}BPP')
            self.color_schemeInput.setCurrentText(data.mode)
            self.formatData.setText(data.format)
            image = QPixmap(f'{self.temp_path}\\temp.png')

        except (IOError, UnidentifiedImageError):
            self.formatData.setText('')

            try:
                new_image = Image.frombytes(codec, (width, height), image_data)

                if rotate == self.local["mirror_h"]:
                    new_image = ImageOps.mirror(new_image)
                elif rotate == self.local["mirror_v"]:
                    new_image = ImageOps.flip(new_image)
                elif rotate == f'90° {self.local["left"]}':
                    new_image = new_image.rotate(-90)
                elif rotate == f'90° {self.local["right"]}':
                    new_image = new_image.rotate(90)
                elif rotate in ('180°', self.local["invert"]):
                    new_image = new_image.rotate(180)
                elif rotate == self.local["negative"]:
                    new_image = new_image.convert(mode='RGB')
                    new_image = ImageOps.invert(new_image)
                    new_image = new_image.convert(mode=codec)
                elif rotate == self.local["grayscale"]:
                    new_image = ImageOps.grayscale(new_image)

                new_image.save(f'{self.temp_path}\\temp.{self.ext}')

            except ValueError as _error:
                self.label_info.setText(f'{self.local["no_byte"]}\n{_error}')

            image = QPixmap(f'{self.temp_path}\\temp.{self.ext}')

        self.graphicsPreview.setPixmap(image.scaled(zoom * image.size()))

    def colorWrapper(self, image_data):

        readCodec = self.color_schemeInput.currentText()
        bpp = self.bppInput.currentText()
        width = int(self.widthInput.value())
        height = int(self.heightInput.value())
        codec = readCodec

        match readCodec:
            case 'RGB' | 'HSV' | 'CMYK' | 'YCbCr' | 'RGBA' | 'RGB' | 'PA' | 'LA' | 'F' | \
                 'RGBX' | 'RGBa' | '1' | 'L' | 'I;16L' | 'I;16B' | 'I' | '':
                self.ext = 'webp'
            case 'LAB':
                self.ext = 'tif'
            case 'HSL':
                codec = 'HSV'
                image_data = converter.HSL2HSV(image_data)
            case 'RBG' | 'GBR' | 'GRB' | 'BRG' | 'BGR' | 'RGBA' | 'RBGA' | 'GBRA' | 'GRBA' | 'BRGA' | 'BGRA' | \
                 'ARGB' | 'ARBG' | 'AGBR' | 'AGRB' | 'ABRG' | 'ABGR' | 'XBGR' | 'XRGB' | 'BGRX':
                image_data = converter.BGR2RGB(image_data, readCodec)
                codec = 'RGB' if bpp == '24BPP' else 'RGBA'
            # case 'DXT1' | 'DXT3' | 'DXT5' | 'DX10' | 'BC5S' | 'BC5U' | 'ATI1' | 'ATI2':
            #     image_data = Image.open(f'{self.temp_path}\\temp.dds')
            #     codec = image_data.mode
            #     image_data.save(f'{self.temp_path}\\temp.png')
            #     image_data = Image.open(f'{self.temp_path}\\temp.png').tobytes()
            #     os.remove(f'{self.temp_path}\\temp.dds')
            case _:
                self.dds_save(width, height, readCodec, image_data)
                self.ext = 'png'

                # Popen(f'data\\readdxt.exe {self.temp_path}\\temp.dds', SW_HIDE).wait()
                Popen(f'data\\texconv -ft PNG {self.temp_path}\\temp.dds', SW_HIDE).wait()

                try:
                    # shutil.move(f'{self.temp_path}\\temp00.tga', f'{self.temp_path}\\temp.tga')
                    shutil.move(f'temp.PNG', f'{self.temp_path}\\temp.png')
                    # image_data = Image.open(f'{self.temp_path}\\temp.tga')
                    image_data = Image.open(f'{self.temp_path}\\temp.png')
                    codec = image_data.mode
                    image_data = image_data.tobytes()

                except FileNotFoundError:
                    self.label_info.setText(f'Write error in codec {readCodec}')
                    codec = 'RGB'

                    with open('log.txt', 'a') as log:
                        log.write(f'Write error in codec {readCodec}\n')

        return codec, image_data

    def dds_save(self, y, x, codec, data):

        try:
            flags = codec_list.codec_list[codec]['flags']
            cdc = codec_list.codec_list[codec]['codec']
            bpp = codec_list.codec_list[codec]['bpp']
            rgba_mask = codec_list.codec_list[codec]['rgb_mask']
            h_flg = codec_list.codec_list[codec]['head_flg']

            with open(f'{self.temp_path}\\temp.dds', 'wb') as dds_file:
                dds_file.write(b'DDS\x20\x7C\x00\x00\x00' + h_flg +  # DDS Header
                               x.to_bytes(4, byteorder='little') +  # Height
                               y.to_bytes(4, byteorder='little') * 2 +  # width and linear size
                               b'\x01\x00\x00\x00' * 2 + b'\x00' * 44 + b'\x20\x00\x00\x00' +
                               flags + cdc + bpp + rgba_mask + b'\x08\x10\x40\x00' + b'\x00' * 16 + data)
        except (KeyError, ValueError):
            pass

    def file_open(self, reopen=False):

        if not reopen:
            self.file_name = QFileDialog.getOpenFileName(self, 'Open File')[0]

            if os.path.exists(f'{self.temp_path}\\temp.png'):
                os.remove(f'{self.temp_path}\\temp.png')

        if self.file_name:

            if os.path.exists(self.file_name):
                shutil.copy(self.file_name, f'{self.temp_path}\\temp.{self.ext}')
                shutil.copy(self.file_name, self.temp_file)
                self.fname_info.setText(f'{self.local["file_select"]}\n{self.file_name.split("/")[-1]}')
                self.draw_image()
            else:
                self.fname_info.setText(f'{self.local["file"]} {self.file_name}\n{self.local["not_found"]}')

    def save_image(self):

        if os.path.exists(f'{self.temp_path}\\temp.{self.ext}'):
            image = Image.open(f'{self.temp_path}\\temp.{self.ext}')
            name = QFileDialog.getSaveFileName(self, 'Save File', '',
                                               'PNG files (*.png);;'
                                               'WEBP files (*.webp);;'
                                               'JPEG file (*.jpg);;'
                                               'BMP file (*.bmp);;'
                                               'TGA file (*.tga);;'
                                               'TIFF file (*.tif);;'
                                               'Icon file (*.ico);;'
                                               'DDS file (*.dds)')[0]

            if name:
                try:
                    image.save(name)
                    self.label_info.setText(f'{self.local["file_saved"]}\n{name}')
                except (OSError, ValueError) as _error:
                    self.label_info.setText(f'{self.local["save_error"]}\n{_error}')

    def unzip(self):

        if self.compressInput.currentText() not in zip_methods.keys():
            return

        zip_name = self.compressInput.currentText()
        zip_method = zip_methods[zip_name]

        dump_name = zip_name + '.dmp'
        script = (f'"data\\quickbms.exe" -o -a "{zip_method}" '
                  f'"data\\comtype_scan2.bms" '
                  f'"{self.temp_file}" "{self.temp_path}"').replace("/", "\\")

        Popen(script).wait()
        dump_file = os.path.join(self.temp_path, dump_name)

        if os.path.exists(dump_file):
            shutil.move(dump_file, self.temp_file)
            self.draw_image()
            lucky = True
        else:
            lucky = False

        self.timer.start(100)
        self.timer.timeout.connect(lambda: self.clearZip(zip_name, lucky))

    def closeEvent(self, event):
        ext_list = ['bmp', 'png', 'tga', 'webp', 'tif', 'dds']

        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

        for ext in ext_list:

            if os.path.exists(f'{self.temp_path}\\temp.{ext}'):
                os.remove(f'{self.temp_path}\\temp.{ext}')

    def hide_show_setting(self):

        if self.hide_setting:
            self.langInput.show()
            self.langLabel.show()
            self.formLayoutWidget.setGeometry(QRect(10, 20, 230, 320))
        else:
            self.langInput.hide()
            self.langLabel.hide()
            self.formLayoutWidget.setGeometry(QRect(10, 20, 230, 290))

        self.hide_setting = not self.hide_setting

    def change_lang(self):
        lll = self.langInput.currentText()
        shutil.copy(f'data/local/{self.lng_list[lll]}', f'lang.json')

        with open(f'lang.json', 'r', encoding='utf-8') as json_file:
            self.local = json.load(json_file)

        self.retranslateUi(self)

    def resizeEvent(self, event):
        x = event.size().width()
        y = event.size().height()

        if x < 800:
            self.resize(800, y)
        elif y < 560:
            self.resize(x, 570)
        else:
            self.openButton.setGeometry(QRect(30, y - 100, 160, 30))
            self.saveButton.setGeometry(QRect(30, y - 60, 160, 30))
            self.tabWidget.setGeometry(QRect(250, 0, x - 260, y - 10))
            self.reOpenButton.setGeometry(QRect(190, y - 100, 30, 30))
            self.settingButton.setGeometry(QRect(190, y - 60, 30, 30))
            self.imageScrollArea.setGeometry(QRect(0, 0, x - 265, y - 35))
            self.label_info.setGeometry(QRect(10, y - 210, 230, 50))
            self.fname_info.setGeometry(QRect(10, y - 150, 230, 40))

    def clearZip(self, zip_name, lucky):

        if self.compressInput.currentText() != self.local["no_zip"]:
            self.compressInput.setCurrentText(self.local["no_zip"])
            self.timer.stop()

        if lucky:
            self.label_info.setText(f'{self.local["algorythm"]} {zip_name}\n{self.local["applied"]}')
        else:
            self.label_info.setText(f'{self.local["a_not_applied"]} {zip_name}')

    def dec2hex(self):
        value = self.offsetInput.value()
        self.offset_hexData.setText(f'0x{value:x}')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
