'''
VDFClasses Python File

This contains all classes used by the Addon.
'''

import struct
import os


def safe_decode_ascii(raw):
    """Decode a bytes field as ASCII, ignoring non-ASCII garbage."""
    if isinstance(raw, bytes):
        return raw.decode('ascii', errors='ignore').strip('\0')
    return str(raw).strip('\0')


class VDFHeader:
    def __init__(self):
        self.binstring = '=4si4sii'
        self.binlength = 20

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.BWDHeader = array[0]
        self.BWDVersion = array[1]
        self.REVHeader = array[2]
        self.SectionLength = array[3]
        self.Unknown = array[4]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, b'BWD2', 8, b'REV', 12, 7)
        fileHandle.write(buffer)
        return self.binlength + position


class VDFCHeader:
    def __init__(self):
        self.binstring = '=4si16sii5ffffi'
        self.binlength = 68

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.headername = safe_decode_ascii(array[0])
        self.sectionsize = array[1]
        self.name = safe_decode_ascii(array[2])
        self.vehicletype = array[3]
        self.vehiclesize = array[4]
        self.lod1dist = array[5]
        self.lod2dist = array[6]
        self.lod3dist = array[7]
        self.lod4dist = array[8]
        self.lod5dist = array[9]
        self.mass = array[10]
        self.multiplyer = array[11]
        self.drag = array[12]
        self.null = array[13]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(
            self.binstring,
            buffer,
            0,
            b'VDFC',
            self.binlength,
            bytes(self.name, 'ascii'),
            self.vehicletype,
            self.vehiclesize,
            self.lod1dist,
            self.lod2dist,
            self.lod3dist,
            self.lod4dist,
            self.lod5dist,
            self.mass,
            self.multiplyer,
            self.drag,
            0
        )
        fileHandle.write(buffer)
        return self.binlength + position


class VGEOHeader:
    def __init__(self):
        self.binstring = '=4sIi'
        self.binlength = 12

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.headername = safe_decode_ascii(array[0])
        self.sectionlength = array[1]
        self.geocount = array[2]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, b'VGEO', self.sectionlength, self.geocount)
        fileHandle.write(buffer)
        return position + self.binlength


class GEOData:
    def __init__(self):
        # 7f i i => type:int, geoflags:int
        self.binstring = '=8s12f8s7fii'
        self.binlength = 100


    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.name = safe_decode_ascii(array[0])
        self.matrix = array[1:13]
        self.parent = safe_decode_ascii(array[13])
        self.geocenter = array[14:17]
        self.sphereradius = array[17]
        self.boxhalfheight = array[18:21]
        self.type = array[21]
        self.geoflags = array[22]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(
            self.binstring,
            buffer,
            0,
            bytes(self.name, 'ascii', errors='ignore'),
            *self.matrix,
            bytes(self.parent, 'ascii', errors='ignore'),
            *self.geocenter,
            self.sphereradius,
            *self.boxhalfheight,
            self.type,
            self.geoflags
        )
        fileHandle.write(buffer)
        return position + self.binlength


class ANIMHeader:
    def __init__(self):
        self.binstring = '=4si16s5ii6i'
        self.binlength = 72

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.headername = safe_decode_ascii(array[0])
        self.sectionlength = array[1]
        self.name = safe_decode_ascii(array[2])
        self.elementscount = array[3]
        self.orientationscount = array[4]
        self.rotationcount = array[5]
        self.translation2count = array[6]
        self.positioncount = array[7]
        self.null2 = array[8]
        self.unknown2 = array[9]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(
            self.binstring,
            buffer,
            0,
            b'ANIM',
            self.sectionlength,
            b'.',
            self.elementscount,
            self.orientationscount,
            self.rotationcount,
            self.translation2count,
            self.positioncount,
            0, 0, 0, 0, 0, 0, 0
        )
        fileHandle.write(buffer)
        return position + self.binlength


class ANIMElement:
    def __init__(self):
        self.binstring = '=i32iiiif'
        self.binlength = 148

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.index = array[0]
        self.unknowngeoflag = array[1:32]
        self.start = array[33]
        self.length = array[34]
        self.loop = array[35]
        self.speed = array[36]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(
            self.binstring,
            buffer,
            0,
            self.index,
            *self.unknowngeoflag,
            self.start,
            self.length,
            self.loop,
            self.speed
        )
        fileHandle.write(buffer)
        return position + self.binlength


class ANIMOrientation:
    def __init__(self):
        self.binstring = '=8si12f12f6i'
        self.binlength = 132

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.name = safe_decode_ascii(array[0])
        self.unknown = array[1]
        self.matrix1 = array[2:14]
        self.matrix2 = array[14:26]
        self.rotationindex = array[26]
        self.rotationcount = array[27]
        self.translation2index = array[28]
        self.translation2count = array[29]
        self.positionindex = array[30]
        self.positioncount = array[31]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(
            self.binstring,
            buffer,
            0,
            bytes(self.name, 'ascii', errors='ignore'),
            0,
            *self.matrix1,
            *self.matrix2,
            self.rotationindex,
            self.rotationcount,
            self.translation2index,
            self.translation2count,
            self.positionindex,
            self.positioncount
        )
        fileHandle.write(buffer)
        return position + self.binlength


class ANIMRotation:
    def __init__(self):
        self.binstring = '=i4f'
        self.binlength = 20

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.frame = array[0]
        self.translate = array[1:5]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, int(self.frame), *self.translate)
        fileHandle.write(buffer)
        return position + self.binlength


class ANIMTranslation2:
    def __init__(self):
        self.binstring = '=i3f'
        self.binlength = 16

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.frame = array[0]
        self.translate = array[1:4]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, int(self.frame), *self.translate)
        fileHandle.write(buffer)
        return position + self.binlength


class ANIMPosition:
    def __init__(self):
        self.binstring = '=i3f'
        self.binlength = 16

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.frame = array[0]
        self.translate = array[1:4]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, int(self.frame), *self.translate)
        fileHandle.write(buffer)
        return position + self.binlength


class COLPSection:
    def __init__(self):
        self.binstring = '=4sI12f'
        self.binlength = 56

    def Read(self, fileContent, position):
        """
        Safely read a COLP section.

        If there aren't enough bytes left in the file to read a full COLP
        block, we treat it as missing/truncated and return without raising.
        """
        # Not enough bytes for a full COLP section – treat as missing.
        if position + self.binlength > len(fileContent):
            # Safe defaults: empty collision box
            self.headername = ''
            self.sectionlength = 0
            self.data = [0.0] * 12
            return position  # don't advance past EOF

        import struct
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        # (use safe decode if you prefer, but this matches the existing code)
        self.headername = array[0].decode('ascii').strip('\0')
        self.sectionlength = array[1]
        self.data = array[2:14]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        import struct
        struct.pack_into(
            self.binstring,
            buffer,
            0,
            b'COLP',
            self.binlength,
            *self.data
        )
        fileHandle.write(buffer)
        return position + self.binlength



class SCPSSection:
    def __init__(self):
        self.binstring = '=4s4i'
        self.binlength = 20

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.headername = safe_decode_ascii(array[0])
        self.sectionlength = array[1]
        self.data = array[2:5]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, b'SCPS', 20, 0, 0, 0)
        fileHandle.write(buffer)
        return position + self.binlength


class EXITSection:
    def __init__(self):
        self.binstring = '=4si'
        self.binlength = 8

    def Read(self, fileContent, position):
        array = struct.unpack(self.binstring, fileContent[position:position + self.binlength])
        self.exit = safe_decode_ascii(array[0])
        self.length = array[1]
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, b'EXIT', 8)
        fileHandle.write(buffer)
        return position + self.binlength


class BlenderAnimation:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.type = 'location'


class BlenderObject:
    def __init__(self, object, geodata):
        self.object = object
        self.geo = geodata
        self.parent = geodata.parent
        self.posanim = {}
        self.rotanim = {}
