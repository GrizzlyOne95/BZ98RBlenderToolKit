'''
GEOClasses Python File

This contains all classes used by the Addon.
'''

#Represents a GEO header. It contains important information for reading a complete geo.
class GEOHeader:
    def __init__(self, array):
        if not type(array[0]) is str:
            self.HeaderType = str(array[0],'ascii').strip('\0')
        else:
            self.HeaderType = array[0]
            
        self.Unknown = array[1]
        
        if not type(array[2]) is str:
            self.GEOName = str(array[2],'ascii').strip('\0')
        else:
            self.GEOName = array[2]

        self.Vertices = array[3]
        self.Faces = array[4]
        self.Unknown2 = array[5]
    def Read(self):
        return [bytes(self.HeaderType,'ascii'), self.Unknown, bytes(self.GEOName,'ascii'), self.Vertices, self.Faces, self.Unknown2]

#Represents a GEO vertex
class GEOVertex:
    def __init__(self, array):
        self.x = array[0]
        self.y = array[1]
        self.z = array[2]
    def Read(self):
        return [self.x, self.y, self.z]

#Represents GEONormals    
class GEONormal:
    def __init__(self, array):
        self.x = array[0]
        self.y = array[1]
        self.z = array[2]
    def Read(self):
        return [self.x, self.y, self.z]
        
#GEOUV only exists to help keep track of UVs and is not part of GEOs.   
class GEOUV:
    def __init__(self, array):
        self.u = array[0]
        self.v = array[1]
    def Read(self):
        return [self.u, self.v]

#Represents all GEO faces in a GEO.    
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
        
        if not type(array[10]) is str:
            self.StringHeader = str(array[10],'ascii').strip('\0')
        else:
            self.StringHeader = array[10]
            
        if not type(array[11]) is str:
            self.MapName = str(array[11],'ascii').strip('\0')
        else:
            self.MapName = array[11]
            
        self.Parent = array[12]
        self.Node = array[13]
        self.VertList = []
    def Read(self):
        return [self.Index, self.Vertices, self.r, self.g, self.b, self.x, self.y, self.z, self.d, self.unknown, bytes(self.StringHeader,'ascii'), bytes(self.MapName,'ascii'), self.Parent, self.Node]

#PolygonVert class is for the points that make up a face. 
class PolygonVert:
    def __init__(self, array):
        self.vertID = array[0]
        self.vertID2 = array[1]
        self.u = array[2]
        self.v = array[3]
    def Read(self):
        return [self.vertID, self.vertID2, self.u, self.v]
