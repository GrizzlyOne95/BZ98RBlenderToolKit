import bpy
import importlib

from . import geo_classes
#Reload it just in case something changed!
importlib.reload(geo_classes)

def geoexport(context, filepath, obj):
    Vertices = []
    Normals = []
    Faces = []
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = obj.data
    for vertex in mesh.vertices:
        Vertices.append(geo_classes.GEOVertex([vertex.co.x,vertex.co.z,vertex.co.y]))
        Normals.append(geo_classes.GEONormal([-vertex.normal.x, -vertex.normal.z, -vertex.normal.y]))
    for face in mesh.polygons:
        #Get the basic data about the faces.
        facematerial = ''
        facecolor = [1,1,1]
        if (obj.data.materials != None and len(obj.data.materials) > 0) and face.material_index  != None:
            facematerial = obj.data.materials[face.material_index].MaterialPropertyGroup.MapTexture
            facecolor = obj.data.materials[face.material_index].diffuse_color
        #Create a new face object to be added in the geo we are exporting.
        NewFace = geo_classes.GEOFace([face.index,len(face.vertices),round(255*facecolor[0]),round(255*facecolor[1]),round(255*facecolor[2]),face.center.x,face.center.y,face.center.z,1.0,0,b'\x04\x00\x00',facematerial,0,0,''])
        if mesh.uv_layers.active == None:
            mesh.uv_layers.new()
        #Gather UVs for our face vertices. 
        uv_layer = mesh.uv_layers.active.data
        curvert = 0
        for loop_index in range(face.loop_start, face.loop_start + face.loop_total):
            NewFace.VertList.append(geo_classes.PolygonVert([face.vertices[curvert],face.vertices[curvert],uv_layer[loop_index].uv[0],1.0 - uv_layer[loop_index].uv[1]]))
            curvert = curvert + 1
        #Add the our face to the list.
        Faces.append(NewFace)
    
    import os
    import struct
    with open(filepath, mode='wb') as file: # b is important -> binary
        NewHeader = geo_classes.GEOHeader(['OEG.',69,obj.name,len(Vertices),len(Faces),0])
        buffer = bytearray(36)
        struct.pack_into('=4si16siii', buffer, 0, *NewHeader.Read())
        file.write(buffer)
        for vertex in Vertices:
            buffer = bytearray(12)
            struct.pack_into('=fff', buffer, 0, *vertex.Read())
            file.write(buffer)
        for normal in Normals:
            buffer = bytearray(12)
            struct.pack_into('=fff', buffer, 0, *normal.Read())
            file.write(buffer)
        for face in Faces:
            buffer = bytearray(55)
            struct.pack_into('=iiBBBffffi3s13sii', buffer, 0, *face.Read())
            file.write(buffer)
            for vert in face.VertList:
                buffer = bytearray(16)
                struct.pack_into('=iiff', buffer, 0, *vert.Read())
                file.write(buffer)
    return {'FINISHED'}
        
def export(context, *, filepath):
    geoexport(context, filepath, bpy.context.view_layer.objects.active)
    return {'FINISHED'}
