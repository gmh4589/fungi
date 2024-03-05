

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



