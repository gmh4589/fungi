
import numpy as np


# For 24 and 32 bits
def BGR2RGB(data, color_order: str):
    byte_array = list(data)
    color_order = color_order.upper().replace('X', 'A')

    a = [byte_array[g] for g in
         range(color_order.index('A'), len(byte_array), len(color_order))] if 'A' in color_order else []
    r = [byte_array[d] for d in range(color_order.index('R'), len(byte_array), len(color_order))]
    g = [byte_array[e] for e in range(color_order.index('G'), len(byte_array), len(color_order))]
    b = [byte_array[f] for f in range(color_order.index('B'), len(byte_array), len(color_order))]

    new_data = [item for sublist in (zip(r, g, b, a) if 'A' in color_order else zip(r, g, b)) for item in sublist]
    return bytes(new_data)


def split_bits(bits, block_sizes, bpp=16):
    # Разбиение битов на блоки заданных размеров
    blocks = []

    blocks_blocks = [bits[i:i + bpp] for i in range(0, len(bits), bpp)]

    for blocks_ in blocks_blocks:
        start = 0

        for size in block_sizes:
            block = blocks_[start:start + size]
            block += [0] * (size - len(block))  # Дополнение нулями, если блок короче
            blocks.append(block)
            start += size

    return blocks


def HSL2HSV(data):
    byte_array = bytes(data)
    new_data = []

    try:

        for i in range(0, len(byte_array), 3):
            new_data.append(byte_array[i])
            s_hsl = byte_array[i + 1] / 255
            l_hsl = byte_array[i + 2] / 255

            v_hsv = s_hsl * min(l_hsl, 1 - l_hsl) + l_hsl
            new_data.append(int((2 - 2 * l_hsl / v_hsv) * 255) if v_hsv else 0)
            new_data.append(int(v_hsv * 255))

        return bytes(new_data)

    except IndexError:
        return byte_array


def conv_2BPP(data):
    byte_array = np.frombuffer(data, dtype=np.uint8)
    split_array = np.unpackbits(byte_array[:, np.newaxis], axis=1)[:, -2:].reshape(-1, 8)

    return split_array.tobytes()


def crop_data(data, height, width, colors=4):

    bytes_len = width * height * colors

    if len(data) < bytes_len:
        return b''

    cropped = data[:bytes_len]
    print(len(data), len(cropped))
    return np.frombuffer(cropped, dtype=np.uint8).reshape((height, width, colors))


def crop_color(image_data, height, width, a_order=0):
    image_data = crop_data(image_data, height, width)
    A, R, G, B = image_data[:, :, 0], image_data[:, :, 1], image_data[:, :, 2], image_data[:, :, 3]
    order_map = {0: (R, G, B), 1: (A, G, B), 2: (A, R, B), 3: (A, R, G)}
    rgb_image = np.stack(order_map.get(a_order, (R, G, B)), axis=-1)

    return rgb_image.tobytes()


def R4G4B4G4_to_RGB8(image_data, height, width, order='RGBG'):
    image = crop_data(image_data, height, width, 2)

    if order == 'RGBG':
        R4 = image[:, :, 0] << 4
        G4_1 = image[:, :, 0] >> 4
        B4 = image[:, :, 1] << 4
        G4_2 = image[:, :, 1] >> 4
    elif order == 'GRGB':
        G4_1 = image[:, :, 0] << 4
        R4 = image[:, :, 0] >> 4
        G4_2 = image[:, :, 1] << 4
        B4 = image[:, :, 1] >> 4

    R8 = R4 << 4
    G8 = (G4_1 >> 4) | (G4_2 << 4)
    B8 = B4 << 4

    rgb_image = np.stack((R8, G8, B8), axis=-1)

    return rgb_image.tobytes()


def snorm2unorm(image_data: bytes):
    data = np.array(bytearray(image_data), dtype=np.int16)
    data = data.astype(np.uint8) + 128

    return data.tobytes()


def add_channel(image_data: bytes, height: int, width: int):
    # Преобразуем байты в numpy массив
    image = np.frombuffer(image_data, dtype=np.uint8)[:width * height * 2]
    image = image.reshape((height, width, 2))  # Предполагается, что изображение имеет 2 канала

    # Разделяем каналы
    ch1 = image[:, :, 0]
    ch2 = image[:, :, 1]
    ch3 = np.zeros_like(ch1, dtype=np.uint8)  # Заполняем третий канал нулями

    # Создаем изображение с тремя каналами (RGB)
    rgb_image = np.stack((ch1, ch2, ch3), axis=-1)

    return rgb_image.tobytes()


def to8bit(image_data: bytes, bit=16):
    image = np.frombuffer(image_data, dtype=np.uint16 if bit == 16 else 32)
    image = (image / 256 if bit == 16 else 65536) - 1

    return image.tobytes()
