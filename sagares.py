import io
import glob
import struct
import itertools

def read_rsc_index(stream):
    stream.seek(-8, io.SEEK_END)
    tbl_off, nb_entries = struct.unpack('<2I', stream.read(8))
    assert stream.read() == b''
    stream.seek(tbl_off, io.SEEK_SET)
    return [struct.unpack('<2I', stream.read(8)) for _ in range(nb_entries)]

def unpack(stream, index):
    for off, size in index:
        f.seek(off, io.SEEK_SET)
        yield f.read(size)

def pack_data(outstream, files):
    for data in files:
        pos = outstream.tell()
        outstream.write(data)
        yield pos, len(data)

def pack(outstream, files):
    index = list(pack_data(outstream, files))
    tbl_off, nb_entries = outstream.tell(), len(index)
    for entry in itertools.chain(index, [(tbl_off, nb_entries)]):
        outstream.write(struct.pack('<2I', *entry))

def read_files(files):
    for fname in files:
        with open(fname, 'rb') as f:
            yield f.read()

if __name__ == '__main__':

    # unpack

    with open('ITE.RSC', 'rb') as f:
        index = read_rsc_index(f)
        for idx, data in enumerate(unpack(f, index)):
            with open(f'OUT/RES_{idx:04d}.RES', 'wb') as out:
                out.write(data)

    # pack

#     files = glob.iglob('OUT/*')
#     with open('ITE-NEW.RSC', 'wb') as out:
#         pack(out, read_files(files))
