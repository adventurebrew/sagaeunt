import io
import struct

import numpy as np
from PIL import Image

from graphics import grid

CHAR_COUNT = 256

def parse_font_header(stream):
    max_h, max_w, row_len = struct.unpack('<3H', stream.read(6))
    indices = struct.unpack(f'<{CHAR_COUNT}H', stream.read(CHAR_COUNT * 2))
    widths = struct.unpack(f'<{CHAR_COUNT}B', stream.read(CHAR_COUNT))
    flags = struct.unpack(f'<{CHAR_COUNT}B', stream.read(CHAR_COUNT))
    trackings = struct.unpack(f'<{CHAR_COUNT}B', stream.read(CHAR_COUNT))
    return list(zip(indices, widths, flags, trackings)), (max_h, max_w, row_len), stream.read()

def parse_font(stream):
    header, (max_h, max_w, row_len), chardata = parse_font_header(stream)
    bitmap = np.unpackbits(np.frombuffer(chardata, dtype=np.uint8).reshape(max_h, row_len), axis=1)

    for idx, (index, width, flag, tracking) in enumerate(header):

        # NOTE: nullified assertions
        # assert flag == 0
        # assert width <= tracking, (idx, width, tracking)

        print(idx, index, width, flag, tracking)
        char = bitmap[:, 8 * index:8 * index + width]
        # print('\n'.join(char))

        # make image
        frame = np.zeros((max_h, tracking), dtype=np.uint8)
        bim = Image.fromarray(frame, mode='P')
        npp = np.asarray(char, dtype=np.uint8)
        im = Image.fromarray(npp, mode='P')
        bim.paste(im)

        yield bim

if __name__ == '__main__':
    with open('OUT/RES_0000.RES', 'rb') as f:
    # with open('OUT.RES', 'rb') as f:
        chars = parse_font(f)
        lchars = [(0, 0, im) for im in chars]

    bim = grid.create_char_grid(256, enumerate(lchars))
    palette = [((59 + x) ** 2 * 83 // 67) % 256 for x in range(256 * 3)]
    bim.putpalette(palette)
    bim.save('chars.png')
