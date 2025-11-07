import bpy
import os
import importlib

from . import geo_classes
#Reload it just in case something changed!
importlib.reload(geo_classes)
        
def geoload(context, geofilepath, *, name=None, flip=True, PreserveFaceColors=False):
    #Some variables for file reading. We need to keep track of our results.
    position = 0
    header = None
    verticeslist = []
    normalslist = []
    uvslist = []
    facelist = []

    if not os.path.exists(geofilepath):
        raise Exception(geofilepath + ' was not found!')
        return None

    #Open the GEO file.
    with open(geofilepath, mode='rb') as file: # b is important -> binary
        #Read the file we opened.
        fileContent = file.read()
        #Read the file header.
        import struct
        header = geo_classes.GEOHeader(struct.unpack("=4si16siii", fileContent[position:position+36]))
        uvslist = [None] * header.Vertices
        position = position + 36
        #Read the vertices data next up.
        for i in range(header.Vertices):
            newvertex = geo_classes.GEOVertex(struct.unpack("=fff", fileContent[position:position+12]))
            position = position + 12
            verticeslist.append(newvertex)
        #Read the normals data next up.
        for i in range(header.Vertices):
            newnormal = geo_classes.GEONormal(struct.unpack("=fff", fileContent[position:position+12]))
            position = position + 12
            normalslist.append(newnormal)
        #Read the faces data next up.
        for i in range(header.Faces):
            newface = geo_classes.GEOFace(struct.unpack("=iiBBBffffi3s13sii", fileContent[position:position+55]))
            position = position + 55
            for vert in range(newface.Vertices):
                newvert = geo_classes.PolygonVert(struct.unpack("iiff", fileContent[position:position+16]))
                position = position + 16
                newface.VertList.append(newvert)
            facelist.append(newface)
        #We have all the data now we need to show our results in blender.
        #Get the name we'll use for our new upcoming object.
        if name == None:
            OBJName = header.GEOName
        else:
            OBJName = name
        
        #Create new blender object.
        mesh = bpy.data.meshes.new("mesh")  # add a new mesh
        obj = bpy.data.objects.new(OBJName, mesh)
        
        #Add our new object to the collection.
        bpy.context.collection.objects.link(obj)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        #Add the vertices
        import bmesh
        bm = bmesh.new()
        for i in range(header.Vertices):
            #Create new verts.
            if flip:
                vert = bm.verts.new((verticeslist[i].x, verticeslist[i].z, verticeslist[i].y))
            else:
                vert = bm.verts.new((verticeslist[i].x, verticeslist[i].y, verticeslist[i].z))
            vert.normal = (normalslist[i].x,normalslist[i].y,normalslist[i].z)
            
        #Create the faces.    
        for face in facelist:
            verts = []
            bm.verts.ensure_lookup_table()
            for vert in face.VertList:
                verts.append(bm.verts[vert.vertID])
                uv = geo_classes.GEOUV([vert.u,1.0-vert.v])
                uvslist[vert.vertID] = uv
            #This try block is here to prevent duplicate faces from stopping imports >:D
            try:
                newface = bm.faces.new(verts)
            except:
                pass
                    
        # make the bmesh the object's mesh
        bm.to_mesh(mesh)
        #Destroy the BMesh
        bm.free()  
        
        #Create some blank UVs.
        mesh.uv_layers.new()
        uv_layer = mesh.uv_layers.active.data
        for poly in mesh.polygons:
            #Create UVs   
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                uv_layer[loop_index].uv = (uvslist[mesh.loops[loop_index].vertex_index].u, uvslist[mesh.loops[loop_index].vertex_index].v)
        
        Slots = {}
        #Create materials for all the faces and assign them.
        for i in range(len(facelist)):    
            face = facelist[i]
            #Create and assign materials.
            if len(face.MapName) > 0:
                if PreserveFaceColors:
                    PreservedName = f'{face.MapName}-Color({face.r},{face.g},{face.b})'
                    mat = bpy.data.materials.get(PreservedName)
                    if mat is None:
                        # create material
                        mat = bpy.data.materials.new(name=PreservedName)
                        mat.diffuse_color = (face.r/255,face.g/255,face.b/255,1.0)
                        mat.MaterialPropertyGroup.MapTexture = face.MapName
                    if obj.data.materials.get(PreservedName) == None:
                        Slots[PreservedName] = len(Slots)
                        obj.data.materials.append(mat)
                    mesh.polygons[i].material_index = Slots[PreservedName]
                else:
                    mat = bpy.data.materials.get(face.MapName)
                    if mat is None:
                        # create material
                        mat = bpy.data.materials.new(name=face.MapName)
                        mat.diffuse_color = (face.r/255,face.g/255,face.b/255,1.0)
                        mat.MaterialPropertyGroup.MapTexture = face.MapName
                    if obj.data.materials.get(face.MapName) == None:
                        Slots[face.MapName] = len(Slots)
                        obj.data.materials.append(mat)
                    mesh.polygons[i].material_index = Slots[face.MapName]

        return obj

def load(context, filepath, *, PreserveFaceColors=True):
    #May as well leave if we can't find the GEO file.
    if not os.path.exists(filepath):
        raise filepath + ' was not found!'
        return {'FINISHED'}
    
    geoload(context, filepath, PreserveFaceColors=True)
    
    return {'FINISHED'}
