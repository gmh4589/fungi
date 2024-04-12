import os
from pprint import pprint

codec_list = {}

for file in os.listdir('out'):

    with open('out\\' + file, 'rb') as dds:
        dds.seek(8)
        keys = dds.read(1)
        pixel_format = dds.read(1)
        depth = dds.read(1)
        dds.seek(69, 1)
        rgb = dds.read(4)
        codec = dds.read(4)
        codec_data = dds.read(60 if codec == b'DX10' else 40)
        data = {
            'keys': keys,
            'pixel_format': pixel_format,
            'depth': depth,
            'rgb': rgb,
            'codec': codec,
            'codec_data': codec_data
        }

        codec_list[file.split('.')[0]] = data

pprint(codec_list)
