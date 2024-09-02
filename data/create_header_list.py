import os
from pprint import pprint

with open('dds_tools.py', 'w') as dds_file:

    for file in os.listdir('out'):

        with open('out\\' + file, 'rb') as dds:
            dds.seek(8)
            keys = dds.read(1)
            pixel_format = dds.read(1)
            depth = dds.read(1)
            dds.seek(69, 1)
            rgb = dds.read(4)
            codec = dds.read(4)
            rgb_data = dds.read(25)
            dds.seek(1, 1)
            color_data = dds.read(30 if codec == b'DX10' else 14)

        dds_data = (f"""
    def {file.split('.')[0]}(self):
        self.codec = {codec}
        self.rgb_data = {rgb_data}
        self.codec_data = {color_data}
        self.depth = {depth}
        self.keys = {keys}
        self.pixel_format = {pixel_format}
        self.rgb = {rgb}
        """)
        dds_file.write(dds_data)
