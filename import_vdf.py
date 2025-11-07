import bpy
import importlib
import os
import bmesh
import mathutils

#For testing purposes. Always set to False if not running in script editor.
EditorRun = False
if EditorRun:
    import sys
    #Add our test folder. If you are testing you should change it to your path!
    sys.path.append('C:/Users/Commando950/Desktop/io_scene_bz')
    import vdf_classes
    import import_geo
else:
    from . import vdf_classes
    from . import import_geo
#Reload it just in case something changed!
importlib.reload(vdf_classes)
importlib.reload(import_geo)

def load(context, filepath, *, ImportAnimations=True, PreserveFaceColors=True):
    EXIT = vdf_classes.EXITSection() #We going to be using this class to read through exit sections.
    GEOList = []
    VDFHeader = vdf_classes.VDFHeader()
    VDFC = vdf_classes.VDFCHeader()
    VGEO = vdf_classes.VGEOHeader()
    ANIM = vdf_classes.ANIMHeader()
    ANIMelements = []
    ANIMorientations = {}
    ANIMrotations = []
    ANIMtranslations2 = []
    ANIMpositions = []
    COLP = vdf_classes.COLPSection()

    if not os.path.exists(filepath):
        raise Exception(filepath + ' was not found!')
        return {'FINISHED'}
        
    #Open the VDF file.
    with open(filepath, mode='rb') as file: # b is important -> binary
        #Read the file we opened.
        fileContent = file.read()
        position = 0
        
        #Read the VDF header information.
        position = VDFHeader.Read(fileContent, position)
        #If we don't see some basic matches, we know something is wrong.
        if VDFHeader.BWDHeader != b'BWD2' or VDFHeader.REVHeader != b'REV\0':
            raise Exception('This file is not a VDF file or is corrupted!')
        
        #Read VDFC header.
        position = VDFC.Read(fileContent, position)
        position = EXIT.Read(fileContent, position)
        
        #Read VGEO header.
        position = VGEO.Read(fileContent, position)
        
        for i in range(28):
            for i in range(VGEO.geocount):
                GEO = vdf_classes.GEOData()
                GEO.Read(fileContent, position)
                GEOList.append(GEO)
                position = position + 100
        import struct
        sectionname = struct.unpack('4s',fileContent[position:position+4])
        if sectionname[0] == b'ANIM':
            position = ANIM.Read(fileContent, position)
            for i in range(ANIM.elementscount):
                Element = vdf_classes.ANIMElement()
                position = Element.Read(fileContent, position)
                ANIMelements.append(Element)
            for i in range(ANIM.orientationscount):
                Orientation = vdf_classes.ANIMOrientation()
                position = Orientation.Read(fileContent, position)
                ANIMorientations.update({Orientation.name:Orientation})
            for i in range(ANIM.rotationcount):
                Rotation = vdf_classes.ANIMRotation()
                position = Rotation.Read(fileContent, position)
                ANIMrotations.append(Rotation)
            for i in range(ANIM.translation2count):
                Translation = vdf_classes.ANIMTranslation2()
                position = Translation.Read(fileContent, position)
                ANIMtranslations2.append(Translation)
            for i in range(ANIM.positioncount):
                Position = vdf_classes.ANIMPosition()
                position = Position.Read(fileContent, position)
                ANIMpositions.append(Position)
            position = EXIT.Read(fileContent, position)
        position = EXIT.Read(fileContent, position)
        position = COLP.Read(fileContent, position)
        innermesh = bpy.data.meshes.new("mesh")  # add a new mesh
        innerobj = bpy.data.objects.new('inner_col', innermesh)
        outermesh = bpy.data.meshes.new("mesh")  # add a new mesh
        outerobj = bpy.data.objects.new('outer_col', outermesh)
        YMaxOut,YMaxIn,YMinIn,YMinOut,XMaxOut,XMaxIn,XMinIn,XMinOut,ZMaxOut,ZMaxIn,ZMinIn,ZMinOut = COLP.data
        
        bpy.context.collection.objects.link(innerobj)
        bpy.context.collection.objects.link(outerobj)
        
        #Create mesh for innerbox.
        bminner = bmesh.new()    
       
        for vert in [(XMaxIn,YMaxIn,ZMinIn),(XMaxIn,YMinIn,ZMinIn),(XMinIn,YMinIn,ZMinIn),(XMinIn,YMaxIn,ZMinIn),(XMaxIn,YMaxIn,ZMaxIn),(XMaxIn,YMinIn,ZMaxIn),(XMinIn,YMinIn,ZMaxIn),(XMinIn,YMaxIn,ZMaxIn)]:
            bminner.verts.new(vert)
        
        bminner.to_mesh(innermesh)
        bminner.free
        
        bmouter = bmesh.new()    
       
        for vert in [(XMaxOut,YMaxOut,ZMinOut),(XMaxOut,YMinOut,ZMinOut),(XMinOut,YMinOut,ZMinOut),(XMinOut,YMaxOut,ZMinOut),(XMaxOut,YMaxOut,ZMaxOut),(XMaxOut,YMinOut,ZMaxOut),(XMinOut,YMinOut,ZMaxOut),(XMinOut,YMaxOut,ZMaxOut)]:
            bmouter.verts.new(vert) 
        
        bmouter.to_mesh(outermesh)
        bmouter.free
        
        #Load all the geos we now know about.
        OBJList = {}
        currentlod = 0
        currentgeo = 0
        for GEO in GEOList:          
            if GEO.name[0:4].lower() != 'null':
                geofilename = os.path.dirname(filepath)+'/' + GEO.name + '.geo'
                
                #This code is mostly for Linux. This will allow us to search for a file if it doesn't exist with the file's correct capitalization.
                if not os.path.exists(geofilename):
                    for root, dirs, files in os.walk(os.path.dirname(geofilename)):
                        for afile in files:
                            if (GEO.name + '.geo').lower() == afile.lower():
                                geofilename = os.path.join(os.path.dirname(geofilename), afile.lower())
                                break
                
                #Load the GEO.
                newobj = import_geo.geoload(
                    context, 
                    geofilename, 
                    PreserveFaceColors=PreserveFaceColors
                )

                #Read and assign data/properties to the new object.
                if newobj != None:
                    geolod = currentlod
                    if currentlod == 0:
                        geolod = 1
                    elif currentlod == 4:
                        geolod = 2
                    elif currentlod == 8:
                        geolod= 3
                    else:
                        geolod = 1

                    #Assign the correct GEOType to every object. We need this for later.
                    newobj.GEOPropertyGroup['GEOType'] = GEO.type
                    newobj.GEOPropertyGroup['GEOFlags'] = GEO.geoflags
                    newobj.GEOPropertyGroup['GeoCenterX'] = GEO.geocenter[0]
                    newobj.GEOPropertyGroup['GeoCenterY'] = GEO.geocenter[1]
                    newobj.GEOPropertyGroup['GeoCenterZ'] = GEO.geocenter[2]
                    newobj.GEOPropertyGroup['SphereRadius'] = GEO.sphereradius
                    newobj.GEOPropertyGroup['BoxHalfHeightX'] = GEO.boxhalfheight[0]
                    newobj.GEOPropertyGroup['BoxHalfHeightY'] = GEO.boxhalfheight[1]
                    newobj.GEOPropertyGroup['BoxHalfHeightZ'] = GEO.boxhalfheight[2]
                    blenobj = vdf_classes.BlenderObject(newobj,GEO)
                    blenobj.obj_index = currentgeo
                    blenobj.obj_lod = geolod
                    OBJList.update({GEO.name.lower():blenobj})
            currentgeo = currentgeo + 1
            if currentgeo == VGEO.geocount:
                currentgeo = 0
                currentlod = currentlod + 1
                
        for Model in OBJList.values():
            #Are we not parented to the world and is there a parent that exists?
            if Model.geo.parent.lower() != 'world' and Model.geo.parent.lower() in OBJList:
                #Define what our parent is for easy access.
                Parent = OBJList[Model.geo.parent.lower()]
                
                #Parent object to their parent if it exists.
                #print(Model.geo.name + ' parented to ' + Parent.geo.name)
                Model.object.parent = Parent.object
            #Are we not parented to the world and is there no parent that exists?
            elif Model.geo.parent.lower() != 'world' and not Model.geo.parent.lower() in OBJList:
                Parent = None
                #Define who the parent is.
                stringlist = list(Model.geo.parent.lower())
                stringlist[3] = '1'
                lowerlodparent = "".join(stringlist)
                if lowerlodparent in OBJList.keys(): 
                    Parent = OBJList[lowerlodparent]
                
                #Parent object to their parent if it exists.
                #print(Model.geo.name + ' parented to ' + Parent.geo.name)
                if Parent != None:
                    Model.object.parent = Parent.object
            
        Matrix = mathutils.Matrix
        Vector = mathutils.Vector
        #Position childless things first.
        for Model in OBJList.values():
            if Model.object.parent == None:
                object = Model.object
                geo = Model.geo
                mat = Matrix()
                mat[0][0:3] = geo.matrix[0],geo.matrix[1],geo.matrix[2]
                mat[1][0:3] = geo.matrix[3],geo.matrix[4],geo.matrix[5]
                mat[2][0:3] = geo.matrix[6],geo.matrix[7],geo.matrix[8]
                rotation = mat.to_euler()
                rotation[:] = rotation[0],rotation[2],rotation[1] 
                #Convert the rotation degrees. Battlezone is a little weird with this one. It needs to be flipped to ZYX and then Z and Y need to be flipped. Mind you we also already flipped Z and Y with the geos on importing.
                object.rotation_mode = 'YZX'
                object.rotation_euler = rotation
                #Make sure you flip the position a bit. Its not XYZ, that is for sure.
                object.location = Vector((geo.matrix[9],geo.matrix[11],geo.matrix[10]))

        #Position children to their parents.     
        for Model in OBJList.values():
            if Model.object.parent != None:
                object = Model.object
                geo = Model.geo
                mat = Matrix()
                mat[0][0:3] = geo.matrix[0],geo.matrix[1],geo.matrix[2]
                mat[1][0:3] = geo.matrix[3],geo.matrix[4],geo.matrix[5]
                mat[2][0:3] = geo.matrix[6],geo.matrix[7],geo.matrix[8]
                rotation = mat.to_euler()
                rotation[:] = rotation[0],rotation[2],rotation[1] 
                #Convert the rotation degrees. Battlezone is a little weird with this one. It needs to be flipped to ZYX and then Z and Y need to be flipped. Mind you we also already flipped Z and Y with the geos on importing.
                object.rotation_mode = 'YZX'
                object.rotation_euler = rotation
                #Make sure you flip the position a bit. Its not XYZ, that is for sure.
                object.location = Vector((geo.matrix[9],geo.matrix[11],geo.matrix[10]))
                
        #Take our VDF information and load it into the scene.
        bpy.context.scene.SDFVDFPropertyGroup['Name'] = VDFC.name
        bpy.context.scene.SDFVDFPropertyGroup['VehicleSize'] = VDFC.vehiclesize
        bpy.context.scene.SDFVDFPropertyGroup['VehicleType'] = VDFC.vehicletype
        bpy.context.scene.SDFVDFPropertyGroup['LOD1'] = VDFC.lod1dist
        bpy.context.scene.SDFVDFPropertyGroup['LOD2'] = VDFC.lod2dist
        bpy.context.scene.SDFVDFPropertyGroup['LOD3'] = VDFC.lod3dist
        bpy.context.scene.SDFVDFPropertyGroup['LOD4'] = VDFC.lod4dist
        bpy.context.scene.SDFVDFPropertyGroup['LOD5'] = VDFC.lod5dist
        bpy.context.scene.SDFVDFPropertyGroup['Mass'] = VDFC.mass
        bpy.context.scene.SDFVDFPropertyGroup['CollMult'] = VDFC.multiplyer
        bpy.context.scene.SDFVDFPropertyGroup['DragCoefficient'] = VDFC.drag
        
        #Clear old animation elements if they exist.
        bpy.context.scene.AnimationCollection.clear()
        if ImportAnimations:
            #Take our animation elements and load them into the scene.
            for element in ANIMelements:
                item = bpy.context.scene.AnimationCollection.add()
                item.Index = element.index
                item.Start = element.start
                item.Length = element.length
                item.Loop = element.loop
                item.Speed = element.speed
            
            EndFrame = 0
            
            #Load the animation data we have already read! 
            for Model in OBJList.values():
                geoname = Model.geo.name
                if geoname in ANIMorientations:
                    modelanim = ANIMorientations[geoname]
                    #Check for rotation animation data..
                    if modelanim.rotationcount > 0:
                        for index in range(modelanim.rotationindex,modelanim.rotationindex+modelanim.rotationcount):
                            #mat = Matrix()
                            #mat[0][0:4] = ANIMrotations[index].translate
                            RotQuaternion = mathutils.Quaternion((ANIMrotations[index].translate[0],ANIMrotations[index].translate[1],ANIMrotations[index].translate[3],ANIMrotations[index].translate[2]))
                            RotEuler = RotQuaternion.to_euler('XYZ')
                            Model.object.rotation_mode = 'XYZ'
                            Model.object.rotation_euler = RotEuler
                            Model.object.keyframe_insert("rotation_euler", frame=ANIMrotations[index].frame)
                            if ANIMrotations[index].frame > EndFrame:
                                EndFrame = ANIMrotations[index].frame
                    #Check for position animation data.
                    if modelanim.positioncount > 0:
                        for index in range(modelanim.positionindex,modelanim.positionindex+modelanim.positioncount):
                            Model.object.location = ANIMpositions[index].translate[0],ANIMpositions[index].translate[2],ANIMpositions[index].translate[1]
                            Model.object.keyframe_insert(data_path="location", frame=ANIMpositions[index].frame)
                            if ANIMpositions[index].frame > EndFrame:
                                EndFrame = ANIMpositions[index].frame
                    '''
                    #Edit all curves to be constant. This will magicaly fix all broken animations in blender.
                    fcurves = Model.object.animation_data.action.fcurves
                    for fcurve in fcurves:
                        for kf in fcurve.keyframe_points:
                            kf.interpolation = 'CONSTANT'
                    '''
            
            #Set the animation to the first frame.
            bpy.context.scene.frame_set(0)
            #Start at 0 of course.
            bpy.context.scene.frame_start = 0
            #End at the last frame of the animation.
            bpy.context.scene.frame_end = EndFrame
            
    return {'FINISHED'}
