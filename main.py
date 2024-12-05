import json
import os
import sys
import shutil
from subprocess import Popen, SW_HIDE

from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QRect, QTimer

from PIL import Image, ImageOps, UnidentifiedImageError, ImageFile, ImageFilter

import converter
import codec_list
from tf import Ui_MainWindow
from zip_list import zip_methods
from palette import PaletteSelector

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
        self.bppInput.addItems(['Palette',
                                '1BPP',
                                '2BPP',
                                '4BPP',
                                '8BPP',
                                # '10BPP',
                                '12BPP',
                                '16BPP',
                                '24BPP',
                                '32BPP',
                                # '48BPP',
                                '64BPP',
                                '96BPP',
                                '128BPP',
                                'DirectX',
                                ])
        self.bppInput.setCurrentText('32BPP')
        self.rotateInput.addItems([self.local['no'], f'90° {self.local["left"]}', f'90° {self.local["right"]}', '180°',
                                   self.local['mirror_h'], self.local['mirror_v'], self.local['invert_read'],
                                   self.local["invert"], self.local["negative"], self.local["grayscale"]])

        self.openButton.clicked.connect(self.file_open)
        self.saveButton.clicked.connect(self.save_image)
        self.reOpenButton.clicked.connect(lambda: self.file_open(reopen=True))
        self.settingButton.clicked.connect(self.hide_show_setting)
        self.palette_btn.clicked.connect(self.select_palette)

        self.widthInput.valueChanged.connect(self.draw_image)
        self.heightInput.valueChanged.connect(self.draw_image)
        self.offsetInput.valueChanged.connect(self.draw_image)
        self.zoomInput.valueChanged.connect(self.draw_image)
        self.compressInput.currentIndexChanged.connect(self.unzip)
        self.bppInput.currentIndexChanged.connect(self.createList)
        self.color_schemeInput.currentIndexChanged.connect(self.draw_image)
        self.color_schemeInput.currentTextChanged.connect(self.set_buttons)
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

    @staticmethod
    def select_palette():
        ps = PaletteSelector()
        ps.exec()

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
        # работает: 88
        # проблемы: 36

        currentChange = self.bppInput.currentText()
        # bpp = str(int(int(currentChange.replace('BPP', '')) / 3))

        match currentChange:
            case 'Palette':
                codecsList = ['Palette']
            # 1-bit Grayscale
            case '1BPP':
                codecsList = ['1bit']
            # case '2BPP':
            #     codecsList = ['2bit_grey']
            case '4BPP':
                codecsList = ['4bit_grey']
            case '8BPP':
                codecsList = ['L', 'A8_UNORM', 'R8_SNORM', 'R8_UNORM', 'R8_SINT', 'ATI1',
                              # TODO На проверку:
                              # 'R8_SINT', 'R8_UINT',
                              ]
            case '12BPP':
                codecsList = ['R4G4B4']
            # case '10BPP':
            #     codecsList = ['Y210', 'Y420']
            # 5-bit RGB with 1-bit alpha chanel, R5G6B5, 16-bit Grayscale
            case '16BPP':
                codecsList = ['B5G6R5_UNORM', 'B5G5R5A1_UNORM', 'B4G4R4A4_UNORM', 'R16_FLOAT', 'R16_UNORM', 'LA', 'PA',
                              'I;16L', 'I;16B', 'R8G8_UNORM', 'R8B8_UNORM', 'G8R8_UNORM', 'G8B8_UNORM', 'B8G8_UNORM',
                              'B8R8_UNORM','R8G8_SNORM', 'R8B8_SNORM', 'G8R8_SNORM', 'G8B8_SNORM', 'B8G8_SNORM',
                              'B8R8_SNORM', 'R16_SNORM',
                              # TODO На проверку:
                              # 'Y216', 'Y416', 'R8G8_SINT', 'R8G8_UINT', 'R16_SINT',
                              # 'R16_SNORM', 'R16_UINT', 'G4R4G4B4_UNORM', 'R4G4B4G4_UNORM',
                              ]
            # 8-bit RGB, HSL, HSV, LAB, YCbCr
            case '24BPP':
                codecsList = ['RGB', 'RBG', 'GBR', 'GRB', 'BRG', 'BGR', 'HSV', 'HSL', 'YCbCr', 'LAB', 'ATI2', 'YUV',
                              # TODO На проверку:
                              # 'YUY2',
                              ]
            # 8-bit RGBA, CMYK, 32-bit Grayscale
            case '32BPP':
                codecsList = ['RGBA', 'RBGA', 'GBRA', 'GRBA', 'BRGA', 'BGRA', 'ARGB', 'ARBG', 'AGBR', 'AGRB', 'ABRG',
                              'ABGR', 'CMYK', 'B8G8R8A8_UNORM_SRGB', 'B8G8R8X8_UNORM_SRGB', 'B8G8R8A8_UNORM',
                              'B8G8R8X8_UNORM', 'R10G10B10A2_UNORM', 'R10G10B10_XR_BIAS_A2_UNORM', 'R32_FLOAT',
                              'R8G8B8A8_SNORM', 'I', 'F', 'AYUV',
                              # TODO На проверку:
                              # 'R8G8B8A8_SINT', 'R8G8B8A8_UINT', 'R9G9B9E5_SHAREDEXP',
                              # 'R11G11B10_FLOAT',
                              # 'R16G16_FLOAT', 'R16G16_SINT', 'R16G16_UINT',
                              # 'R32_SINT', 'R32_UINT', 'R16G16_SNORM', 'R16G16_UNORM',
                              ]
            case '64BPP':
                codecsList = ['R16G16B16A16_FLOAT', 'R16G16B16A16_UINT', 'R16G16B16A16_UNORM', 'R16G16B16A16_SNORM',
                              # TODO На проверку:
                              # 'R16G16B16A16_SINT', 'R32G32_FLOAT',
                              # 'R32G32_SINT', 'R32G32_UINT',
                              ]
            case '96BPP':
                codecsList = ['R32G32B32_FLOAT',
                              # TODO На проверку:
                              # 'R32G32B32_SINT', 'R32G32B32_UINT',
                              ]
            case '128BPP':
                codecsList = ['R32G32B32A32_FLOAT',
                              # TODO На проверку:
                              # 'R32G32B32A32_SINT', 'R32G32B32A32_UINT'
                              ]
            case 'DirectX':
                codecsList = ['BC1_UNORM', 'BC2_UNORM', 'BC3_UNORM', 'BC4_SNORM', 'BC4_UNORM', 'BC5_SNORM', 'BC5_UNORM',
                              'BC6H_SF16', 'BC6H_UF16', 'BC7_UNORM', 'BC7_UNORM_SRGB', 'BC1_UNORM_SRGB', 'BC2_UNORM_SRGB',
                              'BC3_UNORM_SRGB',
                              ]
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
            bpp = int(self.bppInput.currentText().replace('BPP', ''))
        except ValueError:
            bpp = 0

        try:

            with open(self.temp_file, 'rb') as temp_image:
                temp_image.seek(offset)

                if not bpp:
                    image_data = temp_image.read()
                else:
                    image_data = temp_image.read(width * height * bpp)

        except FileNotFoundError:
            self.fname_info.setText(self.local["file_not_select"])
            shutil.copy('data\\fungus.png', self.temp_file)

            with open(self.temp_file, 'rb') as temp_image:
                image_data = temp_image.read()

        if rotate in (self.local["invert_read"], self.local["invert"]):
            image_data = bytes(reversed(list(image_data)))

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

        except (IOError, UnidentifiedImageError, NotImplementedError):
            self.formatData.setText('')

            try:
                new_image = Image.frombytes(codec, (width, height), image_data)

                if codec == 'P':
                    try:
                        with open('temp/palette.dat', 'rb') as p_file:
                            pal = sum([[int.from_bytes(p_file.read(1)) for _ in range(3)] for _ in range(256)], [])

                        new_image.putpalette(pal)
                    except FileNotFoundError:
                        pass

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
        self.ext = 'webp'
        image_data = converter.snorm2unorm(image_data) if '_SNORM' in readCodec else image_data

        match readCodec:

            case 'RGB' | 'HSV' | 'CMYK' | 'YCbCr' | 'RGBA' | 'RGB' | 'PA' | 'LA' | 'F' | \
                 'RGBX' | 'RGBa' | 'L' | 'I;16L' | 'I;16B' | 'I' | '':
                pass
            case 'ATI1' | 'ATI2' | 'BC5_SNORM' | 'BC5_UNORM' | 'B4G4R4A4_UNORM':
                self.dds_save(width, height, readCodec)
                image = Image.open(f'{self.temp_path}\\temp.dds')
                image.save(f'{self.temp_path}\\temp.webp')
            case '1bit':
                codec = '1'
            case '4bit_grey' | '8bit_grey':
                # 'R4G4B4' | '2bit_grey' |
                bit = int(readCodec[0])

                # for sym in readCodec:
                #
                #     try:
                #         bit += int(sym)
                #     except ValueError:
                #         pass

                self.bmp_save(width, height, bit)
                self.ext = 'bmp'
                image_data = Image.open(f'{self.temp_path}\\temp.{self.ext}')
                codec = image_data.mode
                image_data = image_data.tobytes()
            case 'LAB':
                self.ext = 'tif'
            case 'AYUV':
                codec = 'YCbCr'

                try:
                    image_data = image_data[:height * width * 4]
                    image_data = converter.crop_color(bytes(reversed(list(image_data))), height, width, 0)
                    new_image = Image.frombytes(codec, (width, height), image_data).rotate(180)
                    image_data = new_image.tobytes()
                except TypeError:
                    pass

            case 'G4R4G4B4_UNORM' | 'R4G4B4G4_UNORM':
                codec = 'RGB'
                order = readCodec.replace('_UNORM', '').replace('4', '')
                image_data = converter.R4G4B4G4_to_RGB8(image_data, height, width, order)
            case 'YCbCr' | 'YUV':
                codec = 'YCbCr'
            case 'HSL':
                codec = 'HSV'
                image_data = converter.HSL2HSV(image_data)
            case 'RBG' | 'GBR' | 'GRB' | 'BRG' | 'BGR' | 'RGBA' | 'RBGA' | 'GBRA' | 'GRBA' | 'BRGA' | 'BGRA' | \
                 'ARGB' | 'ARBG' | 'AGBR' | 'AGRB' | 'ABRG' | 'ABGR' | 'XBGR' | 'XRGB' | 'BGRX':
                image_data = converter.BGR2RGB(image_data, readCodec)
                codec = 'RGB' if bpp == '24BPP' else 'RGBA'
            case 'Palette':
                codec = 'P'
            case 'R8G8_UNORM' | 'R8B8_UNORM' | 'G8R8_UNORM' | 'G8B8_UNORM' | 'B8G8_UNORM' | 'B8R8_UNORM' | \
                 'R8G8_SNORM' | 'R8B8_SNORM' | 'G8R8_SNORM' | 'G8B8_SNORM' | 'B8G8_SNORM' | 'B8R8_SNORM':
                image_data = converter.add_channel(image_data, height, width)
                color_order = readCodec.replace('_UNORM', '').replace('_SNORM', '').replace('8', '')
                color_order += 'R' if 'R' not in color_order else ('G' if 'G' not in color_order else 'B')
                image_data = converter.BGR2RGB(image_data, color_order)
                codec = 'RGB'
                image = Image.frombytes(codec, (width, height), image_data)

                image.save(f'{self.temp_path}\\temp.webp')

            case _:
                self.dds_save(width, height, readCodec)

                try:

                    if '_SNORM' in readCodec:
                        self.dds_save(width, height,readCodec.replace('_S', '_U'), image_data)

                    self.ext = 'png'
                    Popen('"data/texconv -ft PNG" {self.temp_path}\\temp.dds', SW_HIDE).wait()
                    shutil.move('temp.PNG', f'{self.temp_path}\\temp.{self.ext}')

                    image_data = Image.open(f'{self.temp_path}\\temp.{self.ext}')

                    if '_SNORM' in readCodec:
                        image_data = image_data.filter(ImageFilter.MedianFilter)

                    codec = image_data.mode
                    image_data = image_data.tobytes()

                except FileNotFoundError:
                    self.label_info.setText(f'Write error in codec {readCodec}')
                    codec = 'RGB'

                    with open('log.txt', 'a') as log:
                        log.write(f'Write error in codec {readCodec}\n')

        return codec, image_data

    def set_buttons(self):

        if self.color_schemeInput.currentText() == 'Palette':
            self.palette_btn.setGeometry(QRect(30, 430, 160, 30))
        else:
            self.palette_btn.setGeometry(QRect(30000, 30000, 160, 30))

    def dds_save(self, y, x, codec, image_data=None):

        if image_data is None:
            with open(f'{self.temp_path}\\image.dat', 'rb') as temp_dt:
                temp_dt.seek(int(self.offsetInput.value()))
                image_data = temp_dt.read()

        try:
            dds_image = codec_list.DDSCreator()
            dds_image.dds_save(y, x, codec, f'{self.temp_path}\\temp', image_data)

        except (KeyError, ValueError) as error:
            print(f'{error} Something wrong...')
            pass

    def bmp_save(self, x, y, b):
        print(b)

        with open(f'{self.temp_path}\\image.dat', 'rb') as temp_dt:
            temp_dt.seek(int(self.offsetInput.value()))
            image_data = temp_dt.read()

        # if b == 2:
        #     image_data = converter.conv_2BPP(image_data)
        #     b = 4

        with open(f'{self.temp_path}\\temp.bmp', 'wb') as bmp_file:
            bmp_file.write(b'BM' + (len(image_data) + 0x36).to_bytes(4, byteorder='little') +
                           b'\x00\x00\x00\x00\x36\x00\x00\x00\x28\x00\x00\x00' +
                           x.to_bytes(4, byteorder='little') +
                           y.to_bytes(4, byteorder='little') + b'\x01\x00' +
                           b.to_bytes(2, byteorder='little') + b'\x00\x00\x00\x00' +
                           len(image_data).to_bytes(4, byteorder='little') + (b'\x00' * 16) +
                           image_data)

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
        ext_list = ['bmp', 'png', 'tga', 'webp', 'tif', 'dds', 'dat']

        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

        if os.path.exists(f'{self.temp_path}\\palette.dat'):
            os.remove(f'{self.temp_path}\\palette.dat')

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

            if self.color_schemeInput.currentText() == 'Palette':
                self.palette_btn.setGeometry(QRect(30, y - 140, 160, 30))
            else:
                self.palette_btn.setGeometry(QRect(30000, 30000, 160, 30))

            self.openButton.setGeometry(QRect(30, y - 100, 160, 30))
            self.saveButton.setGeometry(QRect(30, y - 60, 160, 30))
            self.tabWidget.setGeometry(QRect(250, 0, x - 260, y - 10))
            self.reOpenButton.setGeometry(QRect(190, y - 100, 30, 30))
            self.settingButton.setGeometry(QRect(190, y - 60, 30, 30))
            self.imageScrollArea.setGeometry(QRect(0, 0, x - 265, y - 35))
            self.label_info.setGeometry(QRect(10, y - 240, 230, 50))
            self.fname_info.setGeometry(QRect(10, y - 190, 230, 40))

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
