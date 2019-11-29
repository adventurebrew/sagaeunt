import io
import struct
from itertools import zip_longest

import numpy as np
from PIL import Image

from graphics import grid

CHAR_COUNT = 256

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def parse_font_header(stream):
    max_h, max_w, row_len = struct.unpack('<3H', stream.read(6))
    indices = struct.unpack(f'<{CHAR_COUNT}H', stream.read(CHAR_COUNT * 2))
    widths = struct.unpack(f'<{CHAR_COUNT}B', stream.read(CHAR_COUNT))
    flags = struct.unpack(f'<{CHAR_COUNT}B', stream.read(CHAR_COUNT))
    trackings = struct.unpack(f'<{CHAR_COUNT}B', stream.read(CHAR_COUNT))
    return list(zip(indices, widths, flags, trackings)), (max_h, max_w, row_len), stream.read()

def get_charline(chardata, off, byte_len):
    charline = chardata[off:off + byte_len]
    return list(''.join(f'{x:08b}' for x in charline).replace('0', '_').replace('1', '@').encode())

def parse_font(stream):
    header, (max_h, max_w, row_len), chardata = parse_font_header(stream)

    char = [get_charline(chardata, i * row_len, row_len) for i in range(max_h)]
    assert not chardata[row_len * max_h:]
    # for line in char:
    #     print(bytes(line).decode())
    # exit(1)

    for idx, (index, width, flag, tracking) in enumerate(header):

        # assert flag == 0

        byte_len = ((width - 1) // 8) + 1
        assert byte_len < row_len, (byte_len, row_len)

        # assert width <= tracking, (idx, width, tracking)

        print(idx, index, width, flag, tracking)
        char = [get_charline(chardata, char_row * row_len + index, byte_len) for char_row in range(max_h)]
        # print('\n'.join(char))

        # make image
        frame = np.full((max_h, tracking), ord('_'), dtype=np.uint8)
        bim = Image.fromarray(frame, mode='P')
        npp = np.asarray(char, dtype=np.uint8)
        im = Image.fromarray(npp, mode='P')
        bim.paste(im)
        yield bim

if __name__ == '__main__':
    with open('OUT/RES_0002.RES', 'rb') as f:
    # with open('OUT.RES', 'rb') as f:
        chars = parse_font(f)
        lchars = [(0, 0, im) for im in chars]

    bim = grid.create_char_grid(256, enumerate(lchars))
    palette = [((59 + x) ** 2 * 83 // 67) % 256 for x in range(256 * 3)]
    bim.putpalette(palette)
    bim.save('chars.png')
