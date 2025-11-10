'''
SDFClasses Python File

This contains all classes used by the Addon.
'''

import struct
import os

def safe_decode_ascii(raw):
    """Decode a bytes field as ASCII, ignoring non-ASCII garbage."""
    if isinstance(raw, bytes):
        return raw.decode('ascii', errors='ignore').strip('\0')
    return str(raw).strip('\0')

class SDFHeader:
    def __init__(self):
       self.binstring = '=4si4sii'
       self.binlength = 20
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.BWDHeader = array[0]
        self.BWDVersion = array[1]
        self.REVHeader = array[2]
        self.SectionLength = array[3]
        self.Unknown = array[4]
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        # Same layout as VDFHeader, but with the SDF-specific "Unknown" field value (8).
        struct.pack_into(self.binstring, buffer, 0, b'BWD2', 8, b'REV', 12, 8)
        fileHandle.write(buffer)
        return self.binlength + position

        
class SDFCHeader:
    def __init__(self):
        self.binstring = '=4si16si5ff13s13s'
        self.binlength = 78
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.headername = safe_decode_ascii(array[0])
        self.sectionsize = array[1]
        self.name = safe_decode_ascii(array[2])
        self.structuretype = array[3]
        self.lod1dist = array[4]
        self.lod2dist = array[5]
        self.lod3dist = array[6]
        self.lod4dist = array[7]
        self.lod5dist = array[8]
        self.defensive = array[9]
        self.explosioneffect = safe_decode_ascii(array[10])
        self.explosionsound = safe_decode_ascii(array[11])
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, 
        b'SDFC', self.binlength, 
        bytes(self.name, 'ascii', errors='ignore'), 
        self.structuretype, 
        self.lod1dist, self.lod2dist, self.lod3dist, self.lod4dist, self.lod5dist,
        self.defensive,
        bytes(self.explosioneffect, 'ascii', errors='ignore'), bytes(self.explosionsound, 'ascii', errors='ignore'))
        fileHandle.write(buffer)
        return position + self.binlength

#Represents our SGEO header.        
class SGEOHeader:
    def __init__(self):
        self.binstring = '=4sIi'
        self.binlength = 12
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.headername = safe_decode_ascii(array[0])
        self.sectionlength = array[1]
        self.geocount = array[2]
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, b'SGEO', self.sectionlength, self.geocount)
        fileHandle.write(buffer)
        return position + self.binlength

#Represents the most important information of a GEO.        
class GEOData:
    def __init__(self):
        # 7f i i i 4f => type:int, geoflags:int, ddr:int
        self.binstring = '=8s12f8s7fiii4f'
        self.binlength = 120
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.name = safe_decode_ascii(array[0])
        self.matrix = array[1:13]
        self.parent = safe_decode_ascii(array[13])
        self.geocenter = array[14:17]
        self.sphereradius = array[17]
        self.boxhalfheight = array[18:21]
        self.type = array[21]
        self.geoflags = array[22]   # now an int
        self.ddr = array[23]
        self.x = array[24]
        self.y = array[25]
        self.z = array[26]
        self.time = array[27]
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(
            self.binstring,
            buffer,
            0,
            bytes(self.name, 'ascii', errors='ignore'),
            self.matrix[0], self.matrix[1], self.matrix[2], self.matrix[3],
            self.matrix[4], self.matrix[5], self.matrix[6], self.matrix[7],
            self.matrix[8], self.matrix[9], self.matrix[10], self.matrix[11],
            bytes(self.parent, 'ascii', errors='ignore'),
            self.geocenter[0], self.geocenter[1], self.geocenter[2],
            self.sphereradius,
            self.boxhalfheight[0], self.boxhalfheight[1], self.boxhalfheight[2],
            self.type,
            self.geoflags,      # packed as int
            self.ddr,
            self.x, self.y, self.z, self.time,
        )
        fileHandle.write(buffer)
        return position + self.binlength


class ANIMHeader:
    def __init__(self):
        # 4s  i   16s   5i         i      6i
        # tag len name counts      null2  unknown2+reserved(5)
        self.binstring = '=4si16s5ii6i'
        self.binlength = 72

        # sane defaults so export works even if exporter doesn't set everything
        self.headername = 'ANIM'
        self.sectionlength = self.binlength
        self.name = ""
        self.elementscount = 0
        self.orientationscount = 0
        self.rotationcount = 0
        self.translation2count = 0
        self.positioncount = 0
        self.null2 = 0
        self.unknown2 = 0
        # 5 reserved ints (we won't really use them)
        self._reserved = [0] * 5

    def Read(self, fileContent, position):
        array = struct.unpack(
            self.binstring,
            fileContent[position:position + self.binlength]
        )
        # 0..2: tag, len, name
        self.headername = safe_decode_ascii(array[0])
        self.sectionlength = array[1]
        self.name = safe_decode_ascii(array[2])
        # 3..7: 5 counts
        self.elementscount      = array[3]
        self.orientationscount  = array[4]
        self.rotationcount      = array[5]
        self.translation2count  = array[6]
        self.positioncount      = array[7]
        # 8: null2
        self.null2   = array[8]
        # 9..14: unknown2 + 5 reserved ints
        self.unknown2 = array[9]
        self._reserved = list(array[10:15])
        return position + self.binlength

    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(
            self.binstring,
            buffer,
            0,
            b'ANIM',
            int(self.sectionlength),
            bytes(self.name or "", 'ascii', errors='ignore'),
            # 5 counts:
            int(self.elementscount),
            int(self.orientationscount),
            int(self.rotationcount),
            int(self.translation2count),
            int(self.positioncount),
            # null2:
            int(self.null2),
            # unknown2 + 5 reserved:
            int(self.unknown2),
            0, 0, 0, 0, 0
        )
        fileHandle.write(buffer)
        return position + self.binlength




class ANIMElement:
    def __init__(self):
        self.binstring = '=i32iiiif'
        self.binlength = 148
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.index = array[0]
        self.unknowngeoflag = array[1:32]
        self.start = array[33]
        self.length = array[34]
        self.loop = array[35]
        self.speed = array[36]
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, self.index, self.unknowngeoflag[0], self.unknowngeoflag[1], self.unknowngeoflag[2], self.unknowngeoflag[3], self.unknowngeoflag[4], self.unknowngeoflag[5], self.unknowngeoflag[6], self.unknowngeoflag[7], self.unknowngeoflag[8], self.unknowngeoflag[9], self.unknowngeoflag[10], self.unknowngeoflag[11], self.unknowngeoflag[12], self.unknowngeoflag[13], self.unknowngeoflag[14], self.unknowngeoflag[15], self.unknowngeoflag[16], self.unknowngeoflag[17], self.unknowngeoflag[18], self.unknowngeoflag[19], self.unknowngeoflag[20], self.unknowngeoflag[21], self.unknowngeoflag[22], self.unknowngeoflag[23], self.unknowngeoflag[24], self.unknowngeoflag[25], self.unknowngeoflag[26], self.unknowngeoflag[27], self.unknowngeoflag[28], self.unknowngeoflag[29], self.unknowngeoflag[30], self.unknowngeoflag[31],
        self.start, self.length, self.loop, self.speed)
        fileHandle.write(buffer)
        return position + self.binlength

class ANIMOrientation:
    def __init__(self):
        self.binstring = '=8si12f12f6i'
        self.binlength = 132
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.name = safe_decode_ascii(array[0])
        self.unknown = array[1]
        self.matrix1 = array[2:14]
        self.matrix2 = array[14:26]
        self.rotationindex = array[26]
        self.rotationcount = array[27]
        self.translation2index = array[28]
        self.translation2count = array[29]
        self.positionindex = array[30]
        self.positioncount = array [31]
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0,
                         bytes(self.name, 'ascii', errors='ignore'),
                         0,
                         self.matrix1[0], self.matrix1[1], self.matrix1[2], self.matrix1[3], self.matrix1[4], self.matrix1[5], self.matrix1[6], self.matrix1[7], self.matrix1[8], self.matrix1[9], self.matrix1[10], self.matrix1[11],
                         self.matrix2[0], self.matrix2[1], self.matrix2[2], self.matrix2[3], self.matrix2[4], self.matrix2[5], self.matrix2[6], self.matrix2[7], self.matrix2[8], self.matrix2[9], self.matrix2[10], self.matrix2[11],
                         self.rotationindex, self.rotationcount, self.translation2index, self.translation2count, self.positionindex, self.positioncount)
        fileHandle.write(buffer)
        return position + self.binlength
    
class ANIMRotation:
    def __init__(self):
        self.binstring = '=i4f'
        self.binlength = 20
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.frame = array[0]
        self.translate = array[1:5]
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, int(self.frame), *self.translate)
        fileHandle.write(buffer)
        return position + self.binlength

#TODO: Figure out what this even does...
class ANIMTranslation2:
    def __init__(self):
        self.binstring = '=i3f'
        self.binlength = 16
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
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
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.frame = array[0]
        self.translate = array[1:4]
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, int(self.frame), *self.translate)
        fileHandle.write(buffer)
        return position + self.binlength

#Represents the collision information on a structure in its own section.        
class COLPSection:
    def __init__(self):
        self.binstring = '=4sI12f' 
        self.binlength = 56
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.headername = safe_decode_ascii(array[0])
        self.sectionlength = array[1]
        self.data = array[2:14]
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, b'COLP', 56, 
        self.data[0], self.data[1], self.data[2], 
        self.data[3], self.data[4], self.data[5], 
        self.data[6], self.data[7], self.data[8], 
        self.data[9], self.data[10], self.data[11])
        fileHandle.write(buffer)
        return position + self.binlength

#DO NOT SEE THIS SECTION
class SCPSSection:
    def __init__(self):
        self.binstring = '=4s4i'
        self.binlength = 20
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.headername = safe_decode_ascii(array[0])
        self.sectionlength = array[1]
        self.data = array[2:5]
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, b'SCPS', 20, 0, 0, 0)
        fileHandle.write(buffer)
        return position + self.binlength

#Just your good old standard exit section.        
class EXITSection:
    def __init__(self):
        self.binstring = '=4si'
        self.binlength = 8
    def Read (self, fileContent, position):
        array = struct.unpack(self.binstring,fileContent[position:position+self.binlength])
        self.exit = safe_decode_ascii(array[0]) #Would you believe it that it is supposed to just say 'EXIT'?
        self.length = array[1]
        return position + self.binlength
    def Write(self, fileHandle, position):
        buffer = bytearray(self.binlength)
        struct.pack_into(self.binstring, buffer, 0, b'EXIT', 8)
        fileHandle.write(buffer)
        return position + self.binlength

#Represents a single trackable animation channel in blender.        
class BlenderAnimation:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.type = 'location'

#Represents all the important information after we import everything.
#Only used for importing.        
class BlenderObject:
    def __init__(self,object,geodata):
        self.object = object
        self.geo = geodata
        self.parent = geodata.parent
        self.posanim = {}
        self.rotanim = {}
