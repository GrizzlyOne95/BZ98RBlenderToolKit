import bpy
import importlib
import os
import bmesh
import mathutils

from . import vdf_classes
from . import import_geo
# Reload it just in case something changed!
importlib.reload(vdf_classes)
importlib.reload(import_geo)


def load(context, filepath, *, ImportGEOs=True, ImportAnimations=True, PreserveFaceColors=True):
    EXIT = vdf_classes.EXITSection()  # We are going to be using this class to read through exit sections.
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

    # Open the VDF file.
    with open(filepath, mode='rb') as file:  # b is important -> binary
        # Read the file we opened.
        fileContent = file.read()
        position = 0

        # Read the VDF header information.
        position = VDFHeader.Read(fileContent, position)
        # If we don't see some basic matches, we know something is wrong.
        if VDFHeader.BWDHeader != b'BWD2' or VDFHeader.REVHeader != b'REV\0':
            raise Exception('This file is not a VDF file or is corrupted!')

        # Read VDFC header.
        position = VDFC.Read(fileContent, position)
        position = EXIT.Read(fileContent, position)

        # Take our VDF information and load it into the scene.
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

        # Read VGEO header.
        position = VGEO.Read(fileContent, position)

        for i in range(28):
            for j in range(VGEO.geocount):
                GEO = vdf_classes.GEOData()
                GEO.Read(fileContent, position)
                GEOList.append(GEO)
                position = position + 100

        import struct

        # Safely handle optional ANIM / EXIT / COLP sections.
        # If there are no bytes left after GEOs, there is nothing else to read.
        if position + 4 > len(fileContent):
            # No ANIM / EXIT / COLP – fall back to empty collision data.
            COLP.data = [0.0] * 12
        else:
            sectionname = struct.unpack('4s', fileContent[position:position + 4])

            # Optional ANIM block (may or may not be present)
            if sectionname[0] == b'ANIM':
                position = ANIM.Read(fileContent, position)
                for i in range(ANIM.elementscount):
                    Element = vdf_classes.ANIMElement()
                    position = Element.Read(fileContent, position)
                    ANIMelements.append(Element)
                for i in range(ANIM.orientationscount):
                    Orientation = vdf_classes.ANIMOrientation()
                    position = Orientation.Read(fileContent, position)
                    ANIMorientations.update({Orientation.name: Orientation})
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

                # EXIT after ANIM, if there is enough data left.
                if position + EXIT.binlength <= len(fileContent):
                    position = EXIT.Read(fileContent, position)

            # EXIT after VGEO (and/or ANIM), if it exists.
            if position + EXIT.binlength <= len(fileContent):
                position = EXIT.Read(fileContent, position)

            # Only read COLP if we have a full header+body and the header matches.
            if position + 4 <= len(fileContent):
                colp_header = struct.unpack('4s', fileContent[position:position + 4])[0]
                if colp_header == b'COLP' and position + COLP.binlength <= len(fileContent):
                    position = COLP.Read(fileContent, position)
                else:
                    # No valid COLP – use an empty collision box.
                    COLP.data = [0.0] * 12
            else:
                # Not enough bytes even for a COLP header.
                COLP.data = [0.0] * 12

        innermesh = bpy.data.meshes.new("mesh")
        innerobj = bpy.data.objects.new('inner_col', innermesh)
        outermesh = bpy.data.meshes.new("mesh")
        outerobj = bpy.data.objects.new('outer_col', outermesh)
        YMaxOut, YMaxIn, YMinIn, YMinOut, XMaxOut, XMaxIn, XMinIn, XMinOut, ZMaxOut, ZMaxIn, ZMinIn, ZMinOut = COLP.data

        bpy.context.collection.objects.link(innerobj)
        bpy.context.collection.objects.link(outerobj)

        # Create mesh for inner box.
        bminner = bmesh.new()
        for vert in [
            (XMaxIn, YMaxIn, ZMinIn),
            (XMaxIn, YMinIn, ZMinIn),
            (XMinIn, YMinIn, ZMinIn),
            (XMinIn, YMaxIn, ZMinIn),
            (XMaxIn, YMaxIn, ZMaxIn),
            (XMaxIn, YMinIn, ZMaxIn),
            (XMinIn, YMinIn, ZMaxIn),
            (XMinIn, YMaxIn, ZMaxIn),
        ]:
            bminner.verts.new(vert)

        bminner.to_mesh(innermesh)
        bminner.free

        bmouter = bmesh.new()
        for vert in [
            (XMaxOut, YMaxOut, ZMinOut),
            (XMaxOut, YMinOut, ZMinOut),
            (XMinOut, YMinOut, ZMinOut),
            (XMinOut, YMaxOut, ZMinOut),
            (XMaxOut, YMaxOut, ZMaxOut),
            (XMaxOut, YMinOut, ZMaxOut),
            (XMinOut, YMinOut, ZMaxOut),
            (XMinOut, YMaxOut, ZMaxOut),
        ]:
            bmouter.verts.new(vert)

        bmouter.to_mesh(outermesh)
        bmouter.free

        if ImportGEOs:
            # Load all the geos we now know about.
            OBJList = {}
            currentlod = 0
            currentgeo = 0
            for GEO in GEOList:
                if GEO.name[0:4].lower() != 'null':
                    geofilename = os.path.dirname(filepath) + '/' + GEO.name + '.geo'

                    # Case-insensitive search for GEO file if needed.
                    if not os.path.exists(geofilename):
                        for root, dirs, files in os.walk(os.path.dirname(geofilename)):
                            for afile in files:
                                if (GEO.name + '.geo').lower() == afile.lower():
                                    geofilename = os.path.join(os.path.dirname(geofilename), afile.lower())
                                    break

                    # Load the GEO.
                    newobj = import_geo.geoload(
                        context,
                        geofilename,
                        PreserveFaceColors=PreserveFaceColors
                    )

                    if newobj is not None:
                        geolod = currentlod
                        if currentlod == 0:
                            geolod = 1
                        elif currentlod == 4:
                            geolod = 2
                        elif currentlod == 8:
                            geolod = 3
                        else:
                            geolod = 1

                        newobj.GEOPropertyGroup['GEOType'] = GEO.type
                        newobj.GEOPropertyGroup['GEOFlags'] = GEO.geoflags
                        newobj.GEOPropertyGroup['GeoCenterX'] = GEO.geocenter[0]
                        newobj.GEOPropertyGroup['GeoCenterY'] = GEO.geocenter[1]
                        newobj.GEOPropertyGroup['GeoCenterZ'] = GEO.geocenter[2]
                        newobj.GEOPropertyGroup['SphereRadius'] = GEO.sphereradius
                        newobj.GEOPropertyGroup['BoxHalfHeightX'] = GEO.boxhalfheight[0]
                        newobj.GEOPropertyGroup['BoxHalfHeightY'] = GEO.boxhalfheight[1]
                        newobj.GEOPropertyGroup['BoxHalfHeightZ'] = GEO.boxhalfheight[2]
                        blenobj = vdf_classes.BlenderObject(newobj, GEO)
                        blenobj.obj_index = currentgeo
                        blenobj.obj_lod = geolod
                        OBJList.update({GEO.name.lower(): blenobj})

                currentgeo = currentgeo + 1
                if currentgeo == VGEO.geocount:
                    currentgeo = 0
                    currentlod = currentlod + 1

            for Model in OBJList.values():
                if Model.geo.parent.lower() != 'world' and Model.geo.parent.lower() in OBJList:
                    Parent = OBJList[Model.geo.parent.lower()]
                    Model.object.parent = Parent.object
                elif Model.geo.parent.lower() != 'world' and Model.geo.parent.lower() not in OBJList:
                    Parent = None
                    stringlist = list(Model.geo.parent.lower())
                    stringlist[3] = '1'
                    lowerlodparent = "".join(stringlist)
                    if lowerlodparent in OBJList.keys():
                        Parent = OBJList[lowerlodparent]
                    if Parent is not None:
                        Model.object.parent = Parent.object

            Matrix = mathutils.Matrix
            Vector = mathutils.Vector

            # Position childless things first.
            for Model in OBJList.values():
                if Model.object.parent is None:
                    obj = Model.object
                    geo = Model.geo
                    mat = Matrix()
                    mat[0][0:3] = geo.matrix[0], geo.matrix[1], geo.matrix[2]
                    mat[1][0:3] = geo.matrix[3], geo.matrix[4], geo.matrix[5]
                    mat[2][0:3] = geo.matrix[6], geo.matrix[7], geo.matrix[8]
                    rotation = mat.to_euler()
                    rotation[:] = rotation[0], rotation[2], rotation[1]
                    obj.rotation_mode = 'YZX'
                    obj.rotation_euler = rotation
                    obj.location = Vector((geo.matrix[9], geo.matrix[11], geo.matrix[10]))

            # Position children to their parents.
            for Model in OBJList.values():
                if Model.object.parent is not None:
                    obj = Model.object
                    geo = Model.geo
                    mat = Matrix()
                    mat[0][0:3] = geo.matrix[0], geo.matrix[1], geo.matrix[2]
                    mat[1][0:3] = geo.matrix[3], geo.matrix[4], geo.matrix[5]
                    mat[2][0:3] = geo.matrix[6], geo.matrix[7], geo.matrix[8]
                    rotation = mat.to_euler()
                    rotation[:] = rotation[0], rotation[2], rotation[1]
                    obj.rotation_mode = 'YZX'
                    obj.rotation_euler = rotation
                    obj.location = Vector((geo.matrix[9], geo.matrix[11], geo.matrix[10]))

        bpy.context.scene.AnimationCollection.clear()
        if ImportGEOs and ImportAnimations:
            for element in ANIMelements:
                item = bpy.context.scene.AnimationCollection.add()
                item.Index = element.index
                item.Start = element.start
                item.Length = element.length
                item.Loop = element.loop
                item.Speed = element.speed

            EndFrame = 0
            for Model in OBJList.values():
                geoname = Model.geo.name
                if geoname in ANIMorientations:
                    modelanim = ANIMorientations[geoname]
                    if modelanim.rotationcount > 0:
                        for index in range(modelanim.rotationindex, modelanim.rotationindex + modelanim.rotationcount):
                            RotQuaternion = mathutils.Quaternion((
                                ANIMrotations[index].translate[0],
                                ANIMrotations[index].translate[1],
                                ANIMrotations[index].translate[3],
                                ANIMrotations[index].translate[2]
                            ))
                            RotEuler = RotQuaternion.to_euler('XYZ')
                            Model.object.rotation_mode = 'XYZ'
                            Model.object.rotation_euler = RotEuler
                            Model.object.keyframe_insert("rotation_euler", frame=ANIMrotations[index].frame)
                            if ANIMrotations[index].frame > EndFrame:
                                EndFrame = ANIMrotations[index].frame

                    if modelanim.positioncount > 0:
                        for index in range(modelanim.positionindex, modelanim.positionindex + modelanim.positioncount):
                            Model.object.location = (
                                ANIMpositions[index].translate[0],
                                ANIMpositions[index].translate[2],
                                ANIMpositions[index].translate[1]
                            )
                            Model.object.keyframe_insert(data_path="location", frame=ANIMpositions[index].frame)
                            if ANIMpositions[index].frame > EndFrame:
                                EndFrame = ANIMpositions[index].frame

            bpy.context.scene.frame_set(0)
            bpy.context.scene.frame_start = 0
            bpy.context.scene.frame_end = EndFrame

    return {'FINISHED'}
