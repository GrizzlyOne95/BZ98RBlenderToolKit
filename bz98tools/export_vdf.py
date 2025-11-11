# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

import bpy
import importlib
import math
import mathutils
import os

from . import vdf_classes
from . import export_geo
#Reload it just in case something changed!
importlib.reload(vdf_classes)
importlib.reload(export_geo)

#Fixes failures to go by battlezone naming conventions.
def fixgeoname(name, lod):
    geofilename = list(name)
    if len(geofilename) > 8:
        geofilename = geofilename[0:8]
    if lod in (1,2,3):
        geofilename[3] = str(lod)
    else:
        geofilename[3] = '3'
    geofilename[4] = '1'
    return "".join(geofilename)
    
def GenerateGEOCollisions(object):
    #Get the active object.
    obj = object
    #Get ready...
    minx,miny,minz,maxx,maxy,maxz,maxoverall = [0.0]*7
    for vert in obj.data.vertices:
        if vert.co.x < minx:
            minx = vert.co.x
        if vert.co.x > maxx:
            maxx = vert.co.x
        if vert.co.y < minz:
            minz = vert.co.y
        if vert.co.y > maxz:
            maxz = vert.co.y
        if vert.co.z < miny:
            miny = vert.co.z
        if vert.co.z > maxy:
            maxy = vert.co.z
        #Get maximum vertice distance to generate sphere radius.
        for value in vert.co:
            if abs(value) > maxoverall:
                maxoverall = abs(value)
                
    obj.GEOPropertyGroup.SphereRadius = maxoverall
    
    obj.GEOPropertyGroup.GeoCenterX = (minx+maxx)/2
    obj.GEOPropertyGroup.GeoCenterY = (miny+maxy)/2
    obj.GEOPropertyGroup.GeoCenterZ = (minz+maxz)/2
    
    if abs(minx-obj.GEOPropertyGroup.GeoCenterX) >= abs(maxx-obj.GEOPropertyGroup.GeoCenterX):
        obj.GEOPropertyGroup.BoxHalfHeightX = abs(minx-obj.GEOPropertyGroup.GeoCenterX)
    else:
        obj.GEOPropertyGroup.BoxHalfHeightX = abs(maxx-obj.GEOPropertyGroup.GeoCenterX)
        
    if abs(miny-obj.GEOPropertyGroup.GeoCenterY) >= abs(maxy-obj.GEOPropertyGroup.GeoCenterY):
        obj.GEOPropertyGroup.BoxHalfHeightY = abs(miny-obj.GEOPropertyGroup.GeoCenterY)
    else:
        obj.GEOPropertyGroup.BoxHalfHeightY = abs(maxy-obj.GEOPropertyGroup.GeoCenterY)
        
    if abs(minz-obj.GEOPropertyGroup.GeoCenterZ) >= abs(maxz-obj.GEOPropertyGroup.GeoCenterZ):
        obj.GEOPropertyGroup.BoxHalfHeightZ = abs(minz-obj.GEOPropertyGroup.GeoCenterZ)
    else:
        obj.GEOPropertyGroup.BoxHalfHeightZ = abs(maxz-obj.GEOPropertyGroup.GeoCenterZ)

def export(context, *, filepath, ExportAnimations=True, ExportVDFOnly=False):
    '''
    We are going to use a bunch of classes to write data and encapsulate it.
    First we'll initialize a bunch of them here.
    '''
    EXIT = vdf_classes.EXITSection() #We going to be using this class to read through exit sections.
    VDFHeader = vdf_classes.VDFHeader()
    VDFC = vdf_classes.VDFCHeader()
    VGEO = vdf_classes.VGEOHeader()
    ANIM = vdf_classes.ANIMHeader()
    COLP = vdf_classes.COLPSection()
    SCPS = vdf_classes.SCPSSection()
    
    NULLGEO = vdf_classes.GEOData()
    NULLGEO.name = 'NULL'
    NULLGEO.matrix = [0]*12
    NULLGEO.parent = 'NULL'
    NULLGEO.geocenter = [0]*3
    NULLGEO.sphereradius = 0
    NULLGEO.boxhalfheight = [0]*3
    NULLGEO.type = 0
    NULLGEO.geoflags = 0
    
    '''
    Variables to keep track of.
    '''
    #Throw special classes designed to keep track of ALL THIS CRAP in a list!
    blenderobjects = {}
    #Inner and Outer collision objects we'll detect later.
    collisioninner = None
    collisionouter = None
    #Animation data that we will read later.
    ANIMElements = []
    ANIMOrientations = []
    ANIMRotations = []
    ANIMTranslations = []
    ANIMPositions = []
    #Counters
    rot_index = 0
    pos_index = 0
    #What is the amount of geo slots needed per LOD? We'll calculate this later.
    lodcount = 0
    
    '''
    Create/Load VDFC information.
    Will be used in the write process later.
    '''
    #Set VDFC information.
    VDFC.name = context.scene.SDFVDFPropertyGroup.Name
    VDFC.vehicletype = context.scene.SDFVDFPropertyGroup.VehicleType
    VDFC.vehiclesize = context.scene.SDFVDFPropertyGroup.VehicleSize
    VDFC.lod1dist = context.scene.SDFVDFPropertyGroup.LOD1
    VDFC.lod2dist = context.scene.SDFVDFPropertyGroup.LOD2
    VDFC.lod3dist = context.scene.SDFVDFPropertyGroup.LOD3
    VDFC.lod4dist = context.scene.SDFVDFPropertyGroup.LOD4
    VDFC.lod5dist = context.scene.SDFVDFPropertyGroup.LOD5
    VDFC.mass = context.scene.SDFVDFPropertyGroup.Mass
    VDFC.multiplyer = context.scene.SDFVDFPropertyGroup.CollMult
    VDFC.drag = context.scene.SDFVDFPropertyGroup.DragCoefficient
    
    '''
    Find collisions
    Find objects and determine/create their data that will be relevant to BZ.
    '''
    Matrix = mathutils.Matrix
    Vector = mathutils.Vector
    for object in bpy.data.objects:
        # --- Failsafe: fix invalid material indices on this object's mesh ---
        mesh = getattr(object, "data", None)
        if hasattr(mesh, "polygons"):
            mat_count = len(mesh.materials)
            if mat_count > 0:
                for poly in mesh.polygons:
                    idx = getattr(poly, "material_index", 0)
                    if idx is None or idx < 0 or idx >= mat_count:
                        print(f"[BZ VDF Export] Warning: invalid material index {idx} on polygon {poly.index} of object {object.name}; resetting to 0.")
                        poly.material_index = 0

        if object.name.lower() in ['inner_col','innercol','inner_collision',"innercollision"]:
            collisioninner = object
            offset = Vector((0.0,0.0,0.0)) - collisioninner.location
            collisioninner.data.transform(mathutils.Matrix.Translation(-offset))
            collisioninner.matrix_world.translation += offset
        elif object.name.lower() in ['outer_col','outercol','outer_collision',"outercollision"]:
            collisionouter = object
            offset = Vector((0.0,0.0,0.0)) - collisionouter.location
            collisionouter.data.transform(mathutils.Matrix.Translation(-offset))
            collisionouter.matrix_world.translation += offset
        else:
            GEO = vdf_classes.GEOData()
            
            #Assume GEO lod is for first lod level. Until we find out otherwise.
            GEO.lod = 1
            #Do we have greater than 5 or 5 exact characters?
            if len(object.name.lower()) >= 5:
                #Greater than 8 characters... we need to skip it.
                if len(object.name.lower()) > 8:
                    continue
                if object.name.lower()[3] == '1':
                    GEO.lod = 1
                elif object.name.lower()[3] == '2':
                    GEO.lod = 2
                elif object.name.lower()[3] == '3':
                    GEO.lod = 3
                else:
                    #We don't know the lod, lets not assume it. Skipping the object.
                    continue
            else:
                #Discard the object. It has less than 5 characters and is incorrectly named.
                continue

            GEO.name = fixgeoname(object.name, GEO.lod).lower()
            GEO.matrix = [0,0,0,0,0,0,0,0,0,0,0,0]
            if object.parent != None:
                if len(object.parent.name.lower()) >= 5 and len(object.parent.name.lower()) <= 8:
                    if object.parent.name.lower()[3] in ['1','2','3']:
                        GEO.parent = fixgeoname(object.parent.name, GEO.lod).lower()
                    else:
                        GEO.parent = 'WORLD'
                else:
                    #Discard the object. It has less than 5 characters and is incorrectly named.
                    GEO.parent = 'WORLD'
            else:
                GEO.parent = 'WORLD'

            # --------------------------------------------------
            # Transform with SCALE baked in (right/up/front/pos)
            # --------------------------------------------------
            euler = mathutils.Euler((0.0, math.radians(45.0),0.0),'YZX')
            euler[:] = object.rotation_euler.x, object.rotation_euler.z, object.rotation_euler.y
            rot_matrix = euler.to_matrix()   # 3x3

            # Make an explicit 3x3 diagonal scale matrix
            sx, sy, sz = object.scale
            scale_mat = mathutils.Matrix((
                (sx, 0.0, 0.0),
                (0.0, sy, 0.0),
                (0.0, 0.0, sz),
            ))

            thematrix = rot_matrix @ scale_mat

            GEO.matrix[0:3] = thematrix[0][0:3]
            GEO.matrix[3:6] = thematrix[1][0:3]
            GEO.matrix[6:9] = thematrix[2][0:3]
            Translation = object.matrix_local.to_translation()
            GEO.matrix[9:12] = Translation.x, Translation.z, Translation.y
            
            if object.GEOPropertyGroup.GenerateCollision:
                GenerateGEOCollisions(object)

            GEO.geocenter = [object.GEOPropertyGroup.GeoCenterX,object.GEOPropertyGroup.GeoCenterY,object.GEOPropertyGroup.GeoCenterZ]
            GEO.sphereradius = object.GEOPropertyGroup.SphereRadius
            GEO.boxhalfheight = [object.GEOPropertyGroup.BoxHalfHeightX,object.GEOPropertyGroup.BoxHalfHeightY,object.GEOPropertyGroup.BoxHalfHeightZ]
            
            GEO.type = object.GEOPropertyGroup.GEOType
            GEO.geoflags = object.GEOPropertyGroup.GEOFlags
            #Increase the counter on how many objects are in the current LOD.
            #NOTE: Used later to determine the count of geos in VGEO. Which is used to determine the max slots per LOD.
            if GEO.lod == 1:
                lodcount = lodcount + 1
            if not ExportVDFOnly:
                #Go ahead and write the .geo.
                export_geo.geoexport(
                    context, 
                    os.path.dirname(filepath)+'/' + GEO.name + '.geo', 
                    object,
                )
            #Special class(BlenderObject) I made for putting object and geo in one nice package to keep track of both.
            BlenderObject = vdf_classes.BlenderObject(object,GEO)
            blenderobjects.update({GEO.name:BlenderObject})
            
    '''
    Load all the keyframes for more specific handling below.
    '''
    for object in blenderobjects.values():
        blobject = object.object
        anim = blobject.animation_data
        # Is there animation data at all?
        if anim is not None and anim.action is not None:
            quat_anim = {}
            has_euler_keys = False
            # Prefer quaternion curves if the object is actually in quaternion mode.
            prefer_quat = (getattr(blobject, "rotation_mode", "XYZ") == 'QUATERNION')
            for curve in anim.action.fcurves:
                data_path = curve.data_path
                for akeyframe in curve.keyframe_points:
                    keyframe = int(akeyframe.co[0])
                    keyvalue = akeyframe.co[1]
                    # Euler rotation curves (only if we don't explicitly prefer quats)
                    if data_path == 'rotation_euler' and not prefer_quat:
                        has_euler_keys = True
                        if keyframe not in object.rotanim:
                            object.rotanim[keyframe] = [0.0, 0.0, 0.0]
                        object.rotanim[keyframe][curve.array_index] = keyvalue
                    # Quaternion rotation curves
                    elif data_path == 'rotation_quaternion':
                        if keyframe not in quat_anim:
                            # Identity quaternion (w, x, y, z)
                            quat_anim[keyframe] = [1.0, 0.0, 0.0, 0.0]
                        quat_anim[keyframe][curve.array_index] = keyvalue
                    # Location curves
                    elif data_path == 'location':
                        if keyframe not in object.posanim:
                            object.posanim[keyframe] = [0.0, 0.0, 0.0]
                        object.posanim[keyframe][curve.array_index] = keyvalue

            # If we have quaternion curves, convert them to Euler
            # - always, when the object is in QUATERNION mode
            # - otherwise, only if we didn't find usable Euler keys
            if quat_anim and (prefer_quat or not has_euler_keys):
                from mathutils import Quaternion
                for frame, quat_vals in quat_anim.items():
                    q = Quaternion(quat_vals)  # (w, x, y, z)
                    # Convert to Euler in Blender's default XYZ order;
                    # later we remap to the Battlezone YZX convention.
                    eul = q.to_euler('XYZ')
                    object.rotanim[frame] = [eul.x, eul.y, eul.z]
    
    '''
    Read the element data in blender and get it ready for writing later.
    '''

    #Load animation elements in blender.
    for item in context.scene.AnimationCollection:
        newelement = vdf_classes.ANIMElement()
        #Set to zero for now for testing.
        if item.Index in [0,1]:
            newelement.unknowngeoflag = [1]*32
        else:
            newelement.unknowngeoflag = [0]*32
        newelement.index = item.Index
        newelement.start = item.Start
        newelement.length = item.Length
        newelement.loop = item.Loop
        newelement.speed = item.Speed
        ANIMElements.append(newelement)
        
    '''
    We need to create orientations for all the objects.
    This will be used later in writing.
    When creating orientations it will also add all the rotation and positions.
    '''

    for object in blenderobjects.values():
        neworientation = vdf_classes.ANIMOrientation()
        neworientation.name = object.geo.name
        neworientation.unknown = 0
        neworientation.matrix1 = [1.00,0.0,0.0,1.00,0.0,0.0,1.00,0.0,0.0,1.00,0.0,0.0]
        neworientation.matrix2 = object.geo.matrix
        if len(object.posanim) > 0:
            neworientation.positionindex = pos_index
        else:
            neworientation.positionindex = 0
        neworientation.positioncount = len(object.posanim)
        neworientation.translation2index = 0
        neworientation.translation2count = 0
        if len(object.rotanim) > 0:
            neworientation.rotationindex = rot_index
        else:
            neworientation.rotationindex = 0
        neworientation.rotationcount = len(object.rotanim)
        ANIMOrientations.append(neworientation)
        for key, array in object.rotanim.items():
            newrotation = vdf_classes.ANIMRotation()
            newrotation.frame = key
            eul = mathutils.Euler((0.0, math.radians(45.0), 0.0), 'YZX')
            eul[:] = array[0],array[2],array[1]
            quaternion = eul.to_quaternion()
            newrotation.translate = quaternion[:]
            rot_index = rot_index + 1
            ANIMRotations.append(newrotation)
        for key, array in object.posanim.items():
            newposition = vdf_classes.ANIMPosition()
            newposition.frame = key
            if object.object.parent != None:
                #Get the parent inverse if it exists and add it on to the animation to create an accurate offset for animations.
                ObjectInverse = object.object.matrix_parent_inverse.to_translation()
                newposition.translate = ObjectInverse.x+array[0],ObjectInverse.z+array[2],ObjectInverse.y+array[1]
            else:
                newposition.translate = array[0],array[2],array[1]
            pos_index = pos_index + 1
            ANIMPositions.append(newposition)
    
    '''
    Reorder objects based on parenting and lods. If they are the wrong order, everything will blow up! 
    PARENT MUST COME BEFORE CHILD!
    '''
    #Make blank blender objects. Seriously this is important.
    NULLBlenderObject = vdf_classes.BlenderObject(None,NULLGEO)
    objects = [[],[],[]]
    objects[0] = [NULLBlenderObject] * lodcount
    objects[1] = [NULLBlenderObject] * lodcount
    objects[2] = [NULLBlenderObject] * lodcount
    orderednames = []
    numindex = 0
    while(True):
        DoBreak = True
        for objectkeyname in list(blenderobjects):
            object = blenderobjects[objectkeyname]
            if object.geo.lod == 1:
                DoBreak = False
                if object.geo.parent.lower() != 'world':
                    #Note the idea is it will skip the object until we actually have its parent in the reordered list.
                    if object.geo.parent in orderednames:
                        objects[0][numindex] = object
                        orderednames.append(fixgeoname(object.geo.name,1))
                        #Get LOD 2 and 3 version if avaliable.
                        if fixgeoname(object.geo.name,2) in blenderobjects:
                            LOD2 = blenderobjects[fixgeoname(object.geo.name,2)]
                            objects[1][numindex] = LOD2
                        if fixgeoname(object.geo.name,3) in blenderobjects:
                            LOD3 = blenderobjects[fixgeoname(object.geo.name,3)]
                            objects[2][numindex] = LOD3
                        del blenderobjects[object.geo.name]
                        numindex = numindex + 1
                else:
                    objects[0][numindex] = object
                    orderednames.append(fixgeoname(object.geo.name.lower(),1))
                    #Get LOD 2 and 3 version if avaliable.
                    if fixgeoname(object.geo.name,2) in blenderobjects:
                        LOD2 = blenderobjects[fixgeoname(object.geo.name,2)]
                        objects[1][numindex] = LOD2
                    if fixgeoname(object.geo.name,3) in blenderobjects:
                        LOD3 = blenderobjects[fixgeoname(object.geo.name,3)]
                        objects[2][numindex] = LOD3
                    del blenderobjects[object.geo.name]
                    numindex = numindex + 1
        if DoBreak:
            break
    
    #Ok, lets get to writing the VDF data.
    with open(filepath, mode='wb') as file: # b is important -> binary
        position = 0
        
        position = VDFHeader.Write(file, position) #Write VDF header.
        
        position = VDFC.Write(file, position) #Write VDFC section.
        position = EXIT.Write(file, position) #End VDFC
        
        #Write VGEO section.
        #Set the VGEO count to the lod with the highest amount of GEOs.
        VGEO.geocount = lodcount
        VGEO.sectionlength = ((VGEO.geocount * 100) * 28) + VGEO.binlength
        position = VGEO.Write(file, position)
        
        #Write geo data. We need to also fill empty slots with empty geo stuff.
        
        #Write LOD1
        for object in objects[0]:
            object.geo.Write(file, position)
        
        #Write blanks!
        for i in range(3):
            for i in range(lodcount):
                NULLGEO.Write(file, position)
                
        #Write LOD2
        for object in objects[1]:
            object.geo.Write(file, position)
        
        #Write blanks! Again...
        for i in range(3):
            for i in range(lodcount):
                NULLGEO.Write(file, position)
                
        #Write LOD3
        for object in objects[2]:
            object.geo.Write(file, position)
            
        #Write EVEN MORE BLANKS! Wow! What a waste of space...
        for i in range(19):
            for i in range(lodcount):
                NULLGEO.Write(file, position)
        
        #Write ANIM header or don't...
        if len(ANIMElements) > 0 and ExportAnimations:
            ANIM.elementscount = len(ANIMElements)
            ANIM.orientationscount = len(ANIMOrientations)
            ANIM.rotationcount = len(ANIMRotations)
            ANIM.translation2count = 0
            ANIM.positioncount = len(ANIMPositions)
            ANIM.sectionlength = (
                ANIM.binlength
                +
                (ANIM.elementscount * 148)
                +
                (ANIM.orientationscount * 132)
                +
                (ANIM.rotationcount * 20)
                +
                (ANIM.translation2count * 16)
                +
                (ANIM.positioncount * 16)
            )
            position = ANIM.Write(file, position)
            
            #Write ANIM elements.
            for element in ANIMElements:
                position = element.Write(file, position)
                
            #Write ANIM orientations. 
            for orientation in ANIMOrientations:
                position = orientation.Write(file, position)
            
            #Write ANIM rotations. 
            for animrotation in ANIMRotations:
                position = animrotation.Write(file, position)
                
            #Write ANIM positions. 
            for animposition in ANIMPositions:
                position = animposition.Write(file, position)
            
            position = EXIT.Write(file, position) #Need an extra exit for animations.
        position = EXIT.Write(file, position) #Need an exit for VGEO
        
        XInMin,XInMax,YInMin,YInMax,ZInMin,ZInMax = [0.0]*6
        XOutMin,XOutMax,YOutMin,YOutMax,ZOutMin,ZOutMax = [0.0]*6
        if collisioninner != None:
            #Set the initial values to an already existing mesh vertice.
            XInMin = collisioninner.data.vertices[0].co.x
            XInMax = collisioninner.data.vertices[0].co.x
            YInMin = collisioninner.data.vertices[0].co.y
            YInMax = collisioninner.data.vertices[0].co.y
            ZInMin = collisioninner.data.vertices[0].co.z
            ZInMax = collisioninner.data.vertices[0].co.z
            for vert in collisioninner.data.vertices:
                if vert.co.x < XInMin:
                    XInMin = vert.co.x
                if vert.co.x > XInMax:
                    XInMax = vert.co.x
                if vert.co.y < YInMin:
                    YInMin = vert.co.y
                if vert.co.y > YInMax:
                    YInMax = vert.co.y
                if vert.co.z < ZInMin:
                    ZInMin = vert.co.z
                if vert.co.z > ZInMax:
                    ZInMax = vert.co.z
        if collisionouter != None:
            #Set the initial values to an already existing mesh vertice.
            XOutMin = collisionouter.data.vertices[0].co.x
            XOutMax = collisionouter.data.vertices[0].co.x
            YOutMin = collisionouter.data.vertices[0].co.y
            YOutMax = collisionouter.data.vertices[0].co.y
            ZOutMin = collisionouter.data.vertices[0].co.z
            ZOutMax = collisionouter.data.vertices[0].co.z
            for vert in collisionouter.data.vertices:
                if vert.co.x < XOutMin:
                    XOutMin = vert.co.x
                if vert.co.x > XOutMax:
                    XOutMax = vert.co.x
                if vert.co.y < YOutMin:
                    YOutMin = vert.co.y
                if vert.co.y > YOutMax:
                    YOutMax = vert.co.y
                if vert.co.z < ZOutMin:
                    ZOutMin = vert.co.z
                if vert.co.z > ZOutMax:
                    ZOutMax = vert.co.z
        
        COLP.data = [YOutMax,YInMax,YInMin,YOutMin,XOutMax,XInMax,XInMin,XOutMin,ZOutMax,ZInMax,ZInMin,ZOutMin]
        position = COLP.Write(file,position)
        position = EXIT.Write(file, position) #End COLP
        
        position = SCPS.Write(file,position)
        position = EXIT.Write(file, position) #END SPCS

    return {'FINISHED'}
