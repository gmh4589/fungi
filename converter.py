import numpy as np
from PIL import Image


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


def AYUV2ARGB(ayuv_bytes, height, width, colors):
    bytes_len = width * height * colors

    if len(ayuv_bytes) < bytes_len:
        return b''

    ayuv_bytes = ayuv_bytes[:bytes_len]
    ayuv_image = np.frombuffer(ayuv_bytes, dtype=np.uint8).reshape((height, width, colors))

    if colors == 4:
        A = ayuv_image[:, :, 0]  # Альфа-канал

    Y = ayuv_image[:, :, colors - 3]
    U = ayuv_image[:, :, colors - 2].astype(np.float32)
    V = ayuv_image[:, :, colors - 1].astype(np.float32)

    R = ((Y + 1.402 * V) / 2.402).clip(0, 255).astype(np.uint8)
    G = ((Y - 0.344136 * U - 0.714136 * V) + 269.85936).clip(0, 255).astype(np.uint8)
    B = ((Y + 1.772 * U) / 2.772).clip(0, 255).astype(np.uint8)

    if colors == 4:
        argb_image = np.stack((R, G, B, A), axis=-1)
    else:
        argb_image = np.stack((R, G, B), axis=-1)

    argb_image = np.flip(argb_image)

    return argb_image.tobytes()
