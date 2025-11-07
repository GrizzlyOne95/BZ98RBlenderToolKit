'''
GEOClasses Python File

This contains all classes used by the Addon.
'''

def safe_decode_ascii(raw):
    """Decode a bytes field as ASCII, ignoring non-ASCII garbage."""
    if isinstance(raw, bytes):
        return raw.decode('ascii', errors='ignore').strip('\0')
    return str(raw).strip('\0')


# Represents a GEO header. It contains important information for reading a complete geo.
class GEOHeader:
    def __init__(self, array):
        # HeaderType (e.g. 'GEO\0')
        if not isinstance(array[0], str):
            self.HeaderType = safe_decode_ascii(array[0])
        else:
            self.HeaderType = array[0]

        self.Unknown = array[1]

        # GEO name
        if not isinstance(array[2], str):
            self.GEOName = safe_decode_ascii(array[2])
        else:
            self.GEOName = array[2]

        self.Vertices = array[3]
        self.Faces = array[4]
        self.Unknown2 = array[5]

    def Read(self):
        return [
            bytes(self.HeaderType, 'ascii', errors='ignore'),
            self.Unknown,
            bytes(self.GEOName, 'ascii', errors='ignore'),
            self.Vertices,
            self.Faces,
            self.Unknown2,
        ]


# Represents a GEO vertex
class GEOVertex:
    def __init__(self, array):
        self.x = array[0]
        self.y = array[1]
        self.z = array[2]

    def Read(self):
        return [self.x, self.y, self.z]


# Represents GEONormals
class GEONormal:
    def __init__(self, array):
        self.x = array[0]
        self.y = array[1]
        self.z = array[2]

    def Read(self):
        return [self.x, self.y, self.z]


# GEOUV only exists to help keep track of UVs and is not part of GEOs.
class GEOUV:
    def __init__(self, array):
        self.u = array[0]
        self.v = array[1]

    def Read(self):
        return [self.u, self.v]


# Represents all GEO faces in a GEO.
class GEOFace:
    def __init__(self, array):
        self.Index = array[0]
        self.Vertices = array[1]
        self.r = array[2]
        self.g = array[3]
        self.b = array[4]
        self.x = array[5]
        self.y = array[6]
        self.z = array[7]
        self.d = array[8]
        self.unknown = array[9]

        # StringHeader
        if not isinstance(array[10], str):
            self.StringHeader = safe_decode_ascii(array[10])
        else:
            self.StringHeader = array[10]

        # MapName (.map texture name)
        if not isinstance(array[11], str):
            self.MapName = safe_decode_ascii(array[11])
        else:
            self.MapName = array[11]

        self.Parent = array[12]
        self.Node = array[13]
        self.VertList = []

    def Read(self):
        return [
            self.Index,
            self.Vertices,
            self.r,
            self.g,
            self.b,
            self.x,
            self.y,
            self.z,
            self.d,
            self.unknown,
            bytes(self.StringHeader, 'ascii', errors='ignore'),
            bytes(self.MapName, 'ascii', errors='ignore'),
            self.Parent,
            self.Node,
        ]


# PolygonVert class is for the points that make up a face.
class PolygonVert:
    def __init__(self, array):
        self.vertID = array[0]
        self.vertID2 = array[1]
        self.u = array[2]
        self.v = array[3]

    def Read(self):
        return [self.vertID, self.vertID2, self.u, self.v]
