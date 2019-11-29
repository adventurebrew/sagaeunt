import struct

import numpy as np

from graphics import grid

CHAR_COUNT = 256

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

