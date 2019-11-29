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

def read_rsc_index(stream):
    stream.seek(-8, io.SEEK_END)
    tbl_off, nb_entries = struct.unpack('<2I', stream.read(8))
    assert stream.read() == b''
    stream.seek(tbl_off, io.SEEK_SET)
    return [struct.unpack('<2I', stream.read(8)) for _ in range(nb_entries)]

def parse_font_header(data):
    with io.BytesIO(data) as stream:
        max_h, max_w, row_len = struct.unpack('<3H', stream.read(6))
        indices = struct.unpack(f'<{CHAR_COUNT}H', stream.read(CHAR_COUNT * 2))
        widths = struct.unpack(f'<{CHAR_COUNT}B', stream.read(CHAR_COUNT))
        flags = struct.unpack(f'<{CHAR_COUNT}B', stream.read(CHAR_COUNT))
        trackings = struct.unpack(f'<{CHAR_COUNT}B', stream.read(CHAR_COUNT))
        return list(zip(indices, widths, flags, trackings)), (max_h, max_w, row_len), stream.read()

def get_charline(chardata, off, byte_len):
    charline = chardata[off:off + byte_len]
    return list(''.join(f'{x:08b}' for x in charline).replace('0', '_').replace('1', '@').encode())

def parse_font(data):
    header, (max_h, max_w, row_len), chardata = parse_font_header(data)
    # char = [get_charline(chardata, i * row_len, row_len) for i in range(max_h)]
    # print('\n'.join(char))

    for index, width, flag, tracking in header:
        byte_len = ((width - 1) // 8) + 1
        assert byte_len < row_len, (byte_len, row_len)
        print(index, width, flag, tracking)
        char = [get_charline(chardata, char_row * row_len + index, byte_len) for char_row in range(max_h)]
        # print('\n'.join(char))

        # make image
        frame = np.full((max_h, tracking), ord('_'), dtype=np.uint8)
        bim = Image.fromarray(frame, mode='P')
        npp = np.asarray(char, dtype=np.uint8)
        im = Image.fromarray(npp, mode='P')
        bim.paste(im)
        yield bim

def read_chars(frames):
    xpos = 0
    empty = np.zeros((8, 0), dtype=np.uint8)
    for frame in frames:
        if not frame:
            yield 0, 0, 0, 0, empty
        else:
            loc, img = frame
            nd = 1 * (np.asarray(img, dtype=np.uint8) == 64)
            ndr = np.any(nd, axis=0)
            width = 1 + np.where(ndr)[0][-1] if ndr.any() else 0
            assert width <= loc['x2']
            packed = np.packbits(nd[:, :width], axis=1)
            yield xpos, width, 0, loc['x2'], packed
            xpos += packed.shape[1]

if __name__ == '__main__':
    frames = grid.read_image_grid('chars.png')
    frames = [grid.resize_frame(frame) for frame in frames]

    indices, widths, flags, trackings, imgs = zip(*read_chars(frames))
    widths = list(widths)
    max_w = max(widths)
    bitmap = np.hstack(imgs)
    max_h, row_len = bitmap.shape

    with open('OUT.RES', 'wb') as out:
        out.write(struct.pack('<3H', max_h, max_w, row_len))
        out.write(struct.pack(f'<{CHAR_COUNT}H', *indices))
        out.write(struct.pack(f'<{CHAR_COUNT}B', *widths))
        out.write(struct.pack(f'<{CHAR_COUNT}B', *flags))
        out.write(struct.pack(f'<{CHAR_COUNT}B', *trackings))
        out.write(bitmap.tobytes())

    # for line in np.unpackbits(bitmap, axis=1).tolist():
    #     print(''.join(str(x) for x in line).replace('0', '_').replace('1', '@'))

