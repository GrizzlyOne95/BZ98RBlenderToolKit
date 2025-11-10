import bpy

from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        )

from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

if "bpy" in locals():
    import importlib
    if "import_geo" in locals():
        importlib.reload(import_geo)
    if "import_vdf" in locals():
        importlib.reload(import_vdf)
    if "import_sdf" in locals():
        importlib.reload(import_sdf)
    if "export_geo" in locals():
        importlib.reload(export_geo)
    if "export_vdf" in locals():
        importlib.reload(export_vdf)
    if "export_sdf" in locals():
        importlib.reload(export_sdf)

# ----------------------------------------------------------
#  Updated for Blender 4.5.1 compatibility
# ----------------------------------------------------------
bl_info = {
    "name": "Battlezone GEO/VDF/SDF Formats (For Blender 4.5.1)",
    "description": "Import and export GEO/VDF/SDF files from Battlezone (1998 / Redux).",
    "author": "Commando950/DivisionByZero/GrizzlyOne95",
    "version": (0, 9, 5),
    "blender": (4, 5, 1),
    "category": "Import-Export",
    "wiki_url": "https://commando950.neocities.org/docs/BZBlenderAddon/"
}


'''
PROPERTY GROUP DEFINITION CLASSES
Used for custom properties and keeping track of them.
AnimationPropertyGroup - All the properties for an animation element that will be avaliable for editing/storing.
SDFPropertyGroup - The properties of a SDF that will be avaliable for editing/storing.
VDFPropertyGroup - The properties of a VDF that will be avaliable for editing/storing.
GEOPropertyGroup - The properties of a GEO that will be avaliable for editing/storing.
'''
class AnimationPropertyGroup(bpy.types.PropertyGroup):
    Index: bpy.props.IntProperty(
        name = "Index",
        description="Animation index that decides what the animation is for",
        default = 0,
        min = 0,
        max = 1000
    )
    
    Start: bpy.props.IntProperty(
        name = "Start",
        description="First frame of the animation",
        default = 0,
        min = -999999,
        max = 999999
    )
    
    Length: bpy.props.IntProperty(
        name = "Length",
        description="Amount of frames we run and can be negative",
        default = 0,
        min = -999999,
        max = 999999
    )
    
    Loop: bpy.props.IntProperty(
        name = "Loop Count",
        description="How many times will the animation loop?",
        default = 1,
        min = 0,
        max = 100
    )
    
    Speed: bpy.props.FloatProperty(
        name = "Speed",
        description="Speed the animation plays at",
        default = 15.0,
        min = -999999.0,
        max = 999999.0
    )

class SDFVDFPropertyGroup(bpy.types.PropertyGroup):
    #Shared Properties.
    Name: bpy.props.StringProperty(
        name = "Name",
        description="The name inside the file. Kinda unimportant",
        default = 'New Thing',
        maxlen=16
    )
    
    #VDF Properties
    VehicleSize: bpy.props.IntProperty(
        name = "Vehicle Size",
        description="",
        default = 2,
        min = 0,
        max = 10
    )
    
    VehicleType: bpy.props.IntProperty(
        name = "Vehicle Type",
        description="Seems to be set to 1 on most VDFs",
        default = 1,
        min = 0,
        max = 10
    )
    
    Mass: bpy.props.FloatProperty(
        name = "Mass",
        description = "Set how heavy the object is(Default: 1750.0 on many VDFs)",
        default = 1750.0,
        min = 0.0,
        max = 34028234.0
    )
    
    CollMult: bpy.props.FloatProperty(
        name = "Collision Multiplier(?)",
        description = "Unknown(Default: 1.0)",
        default = 1.0,
        min = 0.0,
        max = 34028234.0
    )
    
    DragCoefficient: bpy.props.FloatProperty(
        name = "Drag Coefficient",
        description = "Aerodynamics(?)(Default: 0.0008)",
        default = 0.0008,
        min = 0.0,
        max = 34028234.0
    )
    
    StructureType: bpy.props.IntProperty(
        name = "Structure Type",
        description="Seems to be set to 1 on most VDFs",
        default = 1,
        min = 0,
        max = 10
    )
    
    #SDF Properties here!
    Defensive: bpy.props.FloatProperty(
        name = "Defensive",
        description = "Unknown exactly what this does",
        default = 0.0,
        min = 0.0,
        max = 34028234.0
    )
    
    DeathExplosion: bpy.props.StringProperty(
        name = "",
        description="The .xdf explosion type the building uses",
        default = 'xbldx1.xdf',
        maxlen=13
    )
    
    DeathSound: bpy.props.StringProperty(
        name = "",
        description="The sound the building plays when destroyed",
        default = 'null',
        maxlen=13
    )
    
    #LOD Properties
    LOD1: bpy.props.FloatProperty(
        name = "LOD1 Distance",
        description = "The distance that this LOD(Level of Detail) will load",
        default = 5.0,
        min = 0.0,
        max = 3.40282e+38
    )
    
    LOD2: bpy.props.FloatProperty(
        name = "LOD2 Distance",
        description = "The distance that this LOD(Level of Detail) will load",
        default = 3.40282e+38,
        min = 0.0,
        max = 3.40282e+38
    )
    
    LOD3: bpy.props.FloatProperty(
        name = "LOD3 Distance",
        description = "The distance that this LOD(Level of Detail) will load",
        default = 3.40282e+38,
        min = 0.0,
        max = 3.40282e+38
    )
    
    LOD4: bpy.props.FloatProperty(
        name = "LOD4 Distance",
        description = "The distance that this LOD(Level of Detail) will load",
        default = 3.40282e+38,
        min = 0.0,
        max = 3.40282e+38
    )
    
    LOD5: bpy.props.FloatProperty(
        name = "LOD5 Distance",
        description = "The distance that this LOD(Level of Detail) will load",
        default = 3.40282e+38,
        min = 0.0,
        max = 3.40282e+38
    )

geotypes = []
# Build default "Unknown" entries up through at least the highest known ID (81)
for i in range(0, 82):
    geotypes.append((i, f"{i} - Unknown", ""))


def insertgeotypedata(idx, label):
    geotypes[idx] = (idx, f"{idx} - {label}", "")


# -------------------------------------------------------------------
# GEO CLASS IDs (from Battlezone’s CLASS_ID_* definitions)
# -------------------------------------------------------------------
insertgeotypedata(0,  "NONE (Does nothing, part of main object)")
insertgeotypedata(1,  "HELICOPTER (Crashes game as VDF/SDF – do not use)")
insertgeotypedata(2,  "STRUCTURE1 (Wooden structures, unknown)")
insertgeotypedata(3,  "POWERUP (Crashes game as VDF/SDF)")
insertgeotypedata(4,  "PERSON (Unknown / untested)")
insertgeotypedata(5,  "SIGN (Unknown / untested)")
insertgeotypedata(6,  "VEHICLE (Unknown / untested)")
insertgeotypedata(7,  "SCRAP (Scrap material)")
insertgeotypedata(8,  "BRIDGE (Structure containing floor; likely no extra behavior)")
insertgeotypedata(9,  "FLOOR (Bridge floor; likely no extra behavior)")
insertgeotypedata(10, "STRUCTURE2 (Metal structures)")
insertgeotypedata(11, "SCROUNGE (Faces GEO toward camera)")

# Old “LGT” guess – still unknown, keep for completeness
insertgeotypedata(33, "LGT (Vehicle light? – legacy guess)")

insertgeotypedata(15, "SPINNER (Spinner / rotating geo; usable on VDFs & buildings)")

insertgeotypedata(34, "RADAR (Unknown, likely no effect)")
insertgeotypedata(38, "HEADLIGHT_MASK (Redux headlight bone)")
insertgeotypedata(40, "EYEPOINT (POV / sniper dot / 1st-person origin)")
insertgeotypedata(42, "COM (Center of mass; unused)")

# Legacy geometry “role” IDs
insertgeotypedata(50, "WEAPON (Weapon geometry – legacy)")
insertgeotypedata(51, "ORDNANCE (Ordnance geometry – legacy)")
insertgeotypedata(52, "EXPLOSION (Explosion geometry)")
insertgeotypedata(53, "CHUNK (Chunk geometry)")
insertgeotypedata(54, "SORT_OBJECT (Sorting object)")
insertgeotypedata(55, "NONCOLLIDABLE (Non-collidable geometry)")

# Modern geometry role IDs
insertgeotypedata(60, "VEHICLE_GEOMETRY (Vehicle geometry / body)")
insertgeotypedata(61, "STRUCTURE_GEOMETRY (Structure geometry)")
insertgeotypedata(63, "WEAPON_GEOMETRY (Weapon geometry)")
insertgeotypedata(64, "ORDNANCE_GEOMETRY (Ordnance geometry)")
insertgeotypedata(65, "TURRET_GEOMETRY (X/Y turret rotators, gun towers)")
insertgeotypedata(66, "ROTOR_GEOMETRY (Rotates on A/D thrust)")
insertgeotypedata(67, "NACELLE_GEOMETRY (Thrust/steering nacelle; W/A/S/D + flame)")
insertgeotypedata(68, "FIN_GEOMETRY (Steering fin)")
insertgeotypedata(69, "COCKPIT_GEOMETRY (Cockpit geometry)")

# Hardpoints & emitters
insertgeotypedata(70, "WEAPON_HARDPOINT (* hardpoint, no default powerups) Also Prod Unit Smoke Emitter")
insertgeotypedata(71, "CANNON_HARDPOINT")
insertgeotypedata(72, "ROCKET_HARDPOINT")
insertgeotypedata(73, "MORTAR_HARDPOINT")
insertgeotypedata(74, "SPECIAL_HARDPOINT (where prod unit throws out a build")
insertgeotypedata(75, "FLAME_EMITTER (Visible on full forward thrust). Makes the geo geometry invisible.")
insertgeotypedata(76, "SMOKE_EMITTER")
insertgeotypedata(77, "DUST_EMITTER")

insertgeotypedata(81, "PARKING_LOT (Hangar / supply pad center of effect)")

    
class GEOPropertyGroup(bpy.types.PropertyGroup):
    GenerateCollision: bpy.props.BoolProperty(
        name="Automatically Generate Collisions",
        description="If enabled, will generate collisions for the selected object when exported. Does not generate Outer/Inner collisions, but does generate GEO Center, GEO Projectile Box, and the Sphere Radius. Extremely useful for structures, as they won't have collision otherwise. Everything entered in Blender will be ignored when this is enabled, not for users who want manual tweaking",
        default=True
    )

    GeoCenterX: bpy.props.FloatProperty(
        name = "",
        description="Sets where the center of the GEO is. Used by projectile collision box in SDF",
        default = 0.0,
        min = -50000.0,
        max = 50000.0
    )
    
    GeoCenterY: bpy.props.FloatProperty(
        name = "",
        description="Sets where the center of the GEO is. Used by projectile collision box in SDF",
        default = 0.0,
        min = -50000.0,
        max = 50000.0
    )
    
    GeoCenterZ: bpy.props.FloatProperty(
        name = "",
        description="Sets where the center of the GEO is. Used by projectile collision box in SDF",
        default = 0.0,
        min = -50000.0,
        max = 50000.0
    )
    
    SphereRadius: bpy.props.FloatProperty(
        name = "GEO Sphere Radius",
        description="If set to 0.0 GEO gibs don't even appear. Used in structures as well for deciding what faces you run into. If a GEO face is inside the sphere radius you will likely collide with it",
        default = 3.0,
        min = 0.0,
        max = 50000.0
    )
    
    BoxHalfHeightX: bpy.props.FloatProperty(
        name = "",
        description="Sets the width/length of the projectile collision box for structures",
        default = 0.0,
        min = -50000.0,
        max = 50000.0
    )
    
    BoxHalfHeightY: bpy.props.FloatProperty(
        name = "",
        description="Sets the height of the projectile collision box for structures",
        default = 0.0,
        min = -50000.0,
        max = 50000.0
    )
    
    BoxHalfHeightZ: bpy.props.FloatProperty(
        name = "",
        description="Sets the width/length of the projectile collision box for structures",
        default = 0.0,
        min = -50000.0,
        max = 50000.0
    )

    GEOType: bpy.props.IntProperty(
        name = "GEO Type",
        description="What kind of GEO is this? Very important to set to what you want",
        default = 60,
        min = 0,
        max = 100
    )
    
    GEOFlags: bpy.props.IntProperty(
        name="GEO Flags",
        description="Bitfield of GEO flags (32-bit). Each bit enables a specific Battlezone GEO behavior.",
        default=0,
        min=-2147483648,
        max=2147483647,
    )

    
    SDFDDR: bpy.props.IntProperty(
        name = "DDR",
        description="Unknown what this does. Set to 50000 on most GEOs",
        default = 50000,
        min = 0,
        max = 5000000
    )

    
    SDFX: bpy.props.FloatProperty(
        name = "X",
        description="Controls things like spinner directions and more. Exact features need to be documented",
        default = 0,
        min = -500000.0,
        max = 500000.0
    )
    
    SDFY: bpy.props.FloatProperty(
        name = "Y",
        description="Controls things like spinner directions and more. Exact features need to be documented",
        default = 0,
        min = -500000.0,
        max = 500000.0
    )

    SDFZ: bpy.props.FloatProperty(
        name = "Z",
        description="Controls things like spinner directions and more. Exact features need to be documented",
        default = 0,
        min = -500000.0,
        max = 500000.0
    )
    
    SDFTime: bpy.props.FloatProperty(
        name = "Time",
        description="Unknown. Need documentation",
        default = 0.0,
        min = -500000.0,
        max = 500000.0
    )

class MaterialPropertyGroup(bpy.types.PropertyGroup):
    MapTexture: bpy.props.StringProperty(
        name="Texture",
        description="The name of the .map texture that this material will represent. Do not include .map extension name.",
        default = '',
        maxlen=8
    )

'''
PANEL DEFINITIONS
BattlezoneSDFVDFProperties - Stores all the properties of the current SDF/VDF in the scene tab.
BattlezoneGEOProperties - Stores all the properties of a GEO object in the object tab of objects.
'''
class BattlezoneSDFVDFProperties(bpy.types.Panel):
    bl_idname = "SCENE_PT_BZ_SDFVDF"
    bl_label = "Battlezone SDF/VDF Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        SDFVDFPropertyGroup = scene.SDFVDFPropertyGroup

        layout.prop( SDFVDFPropertyGroup, "Name")
        
        box = layout.box()
        box.label(text="VDF Settings")
        box.prop( SDFVDFPropertyGroup, "VehicleSize")
        box.prop( SDFVDFPropertyGroup, "VehicleType") 
        box.prop( SDFVDFPropertyGroup, "Mass")
        box.prop( SDFVDFPropertyGroup, "CollMult")
        box.prop( SDFVDFPropertyGroup, "DragCoefficient")
        
        box = layout.box()
        box.label(text="SDF Settings")
        box.prop( SDFVDFPropertyGroup, "StructureType")
        box.prop( SDFVDFPropertyGroup, "Defensive")
        box.label(text="Death Explosion")
        box.prop( SDFVDFPropertyGroup, "DeathExplosion")
        box.label(text="Death Sound")
        box.prop( SDFVDFPropertyGroup, "DeathSound")
        
        box = layout.box()
        box.label(text="Level of Detail Settings")
        box.prop( SDFVDFPropertyGroup, "LOD1")
        box.prop( SDFVDFPropertyGroup, "LOD2")
        box.prop( SDFVDFPropertyGroup, "LOD3")
        box.prop( SDFVDFPropertyGroup, "LOD4")
        box.prop( SDFVDFPropertyGroup, "LOD5")

class BattlezoneGEOProperties(bpy.types.Panel):
    bl_idname = "OBJECT_PT_BZ_GEO"
    bl_label = "Battlezone GEO Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        object = context.object
        GEOPropertyGroup = object.GEOPropertyGroup
        
        box = layout.box()
        box.label(text="SDF/VDF GEO Settings")
        box.prop( GEOPropertyGroup, "GEOType")
        box.prop( GEOPropertyGroup, "GEOFlags")
        
        box = layout.box()
        box.label(text="GEO Collision Settings")
        box.prop( GEOPropertyGroup, "GenerateCollision")
        box.label(text="GEO Center X/Y/Z")
        split = box.split()
        split.prop( GEOPropertyGroup, "GeoCenterX")
        split.prop( GEOPropertyGroup, "GeoCenterY")
        split.prop( GEOPropertyGroup, "GeoCenterZ")
        box.label(text="GEO Projectile Collision Box X/Y/Z")
        split = box.split()
        split.prop( GEOPropertyGroup, "BoxHalfHeightX")
        split.prop( GEOPropertyGroup, "BoxHalfHeightY")
        split.prop( GEOPropertyGroup, "BoxHalfHeightZ")
        box.prop( GEOPropertyGroup, "SphereRadius")
        box.operator('bz.generatecollision', text="Generate Collisions", text_ctxt="", translate=True, icon='NONE', emboss=True, depress=False, icon_value=0)
        
        box = layout.box()
        box.label(text="SDF Specific GEO Settings")
        box.prop( GEOPropertyGroup, "SDFDDR")
        box.prop( GEOPropertyGroup, "SDFX")
        box.prop( GEOPropertyGroup, "SDFY")
        box.prop( GEOPropertyGroup, "SDFZ")
        box.prop( GEOPropertyGroup, "SDFTime")
        
class BattlezoneMaterialProperties(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_BZ_GEO"
    bl_label = "Battlezone Material Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        material = context.material
        MaterialPropertyGroup = material.MaterialPropertyGroup
        
        box = layout.box()
        box.label(text="Material Settings")
        box.prop( MaterialPropertyGroup, "MapTexture")
        # Fix: use the current material, not an undefined 'Material'
        box.prop( material, "diffuse_color")
      

'''
Operators
Used for doing actions.
In this case used for creating a new animation element and removing one.
'''
class OPCreateNewElement(bpy.types.Operator):
    bl_idname = "bz.createanimelement"
    bl_label = "Create Element"
    bl_description = "Create a new animation element"

    def execute(self, context):
        item = context.scene.AnimationCollection.add()
        item.Index = len(context.scene.AnimationCollection)-1
        return {'FINISHED'}

class OPDeleteElement(bpy.types.Operator):
    bl_idname = "bz.deleteanimelement"
    bl_label = "Delete Element"
    bl_description = "Delete the currently selected animation element"

    def execute(self, context):
        scene = context.scene
        scene.AnimationCollection.remove(scene.CurAnimation)
        return {'FINISHED'}
        
'''
Operators
Used for doing actions.
In this case used for creating a new animation element and removing one.
'''
class OPGenerateCollision(bpy.types.Operator):
    bl_idname = "bz.generatecollision"
    bl_label = "Generate Collisions"
    bl_description = "Generate Collisions, useful for a manual user"

    def execute(self, context):
        #Get the active object.
        obj = context.view_layer.objects.active
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
        return {'FINISHED'}
        
'''
Animation UIList - Used to make a list of all the animation elements, allowing you to click them to select them.
Animation Panel - Used to hold the UIList, buttons, and all the good stuff including the "animation editor"
'''
class AnimationUIList(bpy.types.UIList):
    bl_idname = "SCENE_UL_Battlezone_ANIM_Element"
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.20)
        split.label(text="Ind: %d" % (item.Index))
        split.label(text="Srt: %d" % (item.Start))
        split.label(text="Len: %d" % (item.Length))
        split.label(text="Loop: %d" % (item.Loop))
        split.label(text="Spd: %d" % (item.Speed))
        
# And now we can use this list everywhere in Blender. Here is a small example panel.
class AnimationPanel(bpy.types.Panel):
    bl_label = "Battlezone Animations"
    bl_idname = "SCENE_PT_Battlezone_ANIM"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        box = layout.box()
        box.label(text="Battlezone Animation Elements")
        box.template_list("SCENE_UL_Battlezone_ANIM_Element", "", scene, "AnimationCollection", scene, "CurAnimation")
        
        box = layout.box()
        box.label(text="Create/Delete element.")
        box.operator('bz.createanimelement', text="New Element", text_ctxt="", translate=True, icon='NONE', emboss=True, depress=False, icon_value=0)
        box.operator('bz.deleteanimelement', text="Delete Element", text_ctxt="", translate=True, icon='NONE', emboss=True, depress=False, icon_value=0)
        
        box = layout.box()
        box.label(text="Element Editor")
        if len(scene.AnimationCollection) > 0:
            box.prop(scene.AnimationCollection[scene.CurAnimation], "Index")
            box.prop(scene.AnimationCollection[scene.CurAnimation], "Start")
            box.prop(scene.AnimationCollection[scene.CurAnimation], "Length")
            box.prop(scene.AnimationCollection[scene.CurAnimation], "Loop")
            box.prop(scene.AnimationCollection[scene.CurAnimation], "Speed")

'''
Import/Export MENUs/UIs for GEO/VDF
Used for importing/exporting
'''
class ImportGEO(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.geo"
    bl_label = "Import GEO"
    bl_description = "Import a Battlezone .GEO file"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".geo"
    filter_glob: StringProperty(
            default="*.geo",
            options={'HIDDEN'},
            )
            
    PreserveFaceColors: BoolProperty(
            name="Preserve Face Colors",
            description="Preserves all colors from the GEOs by making a material for every single face! Each face material will preserve the original GEO color.",
            default=True,
            )

    ImportMapTextures: BoolProperty(
            name="Auto-load .map textures",
            description="Automatically load matching .map files for materials and hook them up as image textures.",
            default=True,
            )
    
    def execute(self, context):
        from . import import_geo
        #Don't pass a ton of stupid stuff to our load function. Who even cares!
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "split_mode",
                                            ))
        
        return import_geo.load(bpy.context, **keywords)
        
class ImportVDF(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.vdf"
    bl_label = "Import VDF"
    bl_description = "Import a Battlezone .VDF file"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".vdf"
    filter_glob: StringProperty(
            default="*.vdf",
            options={'HIDDEN'},
            )

    ImportAnimations: BoolProperty(
            name="Import Animations",
            description="Import Animations for the VDF",
            default=True,
            )

    PreserveFaceColors: BoolProperty(
            name="Preserve Face Colors",
            description="Preserves all colors from the GEOs by making a material for every single face! Each face material will preserve the original GEO color",
            default=True,
            )

    ImportMapTextures: BoolProperty(
            name="Auto-load .map textures",
            description="Automatically load matching .map files for materials and hook them up as image textures.",
            default=True,
            )

    def execute(self, context):
        from . import import_vdf
        #Don't pass a ton of stupid stuff to our load function. Who even cares!
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "split_mode",
                                            ))
        return import_vdf.load(bpy.context, **keywords)
        
class ImportSDF(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.sdf"
    bl_label = "Import SDF"
    bl_description = "Import a Battlezone .SDF file"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".sdf"
    filter_glob: StringProperty(
            default="*.sdf",
            options={'HIDDEN'},
            )

    ImportAnimations: BoolProperty(
            name="Import Animations",
            description="Import Animations for the VDF",
            default=True,
            )

    PreserveFaceColors: BoolProperty(
            name="Preserve Face Colors",
            description="Preserves all colors from the GEOs by making a material for every single face! Each face material will preserve the original GEO color",
            default=True,
            )

    ImportMapTextures: BoolProperty(
            name="Auto-load .map textures",
            description="Automatically load matching .map files for materials and hook them up as image textures.",
            default=True,
            )
    
    def execute(self, context):
        from . import import_sdf
        #Don't pass a ton of stupid stuff to our load function. Who even cares!
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "split_mode",
                                            ))
        return import_sdf.load(bpy.context, **keywords)
        
class ExportGEO(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.geo"  # keep your existing idname if the rest of your addon expects this
    bl_label = "Export GEO"
    bl_description = "Export a Battlezone .GEO file"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".geo"

    filter_glob: StringProperty(
        default="*.geo",
        options={'HIDDEN'},
    )

    # NEW: checkbox for Ogre conversion
    auto_port_ogre: BoolProperty(
        name="Convert export to BZ98R Mesh/Skeleton/Material",
        description=(
            "After writing the GEO, run the Battlezone model porter to create "
            "OGRE .mesh/.skeleton/.material/.dds in the same directory"
        ),
        default=False,
    )

    def execute(self, context):
        from . import export_geo
        from . import ogre_autoport

        keywords = self.as_keywords(ignore=(
            "axis_forward",
            "axis_up",
            "filter_glob",
            "split_mode",
            "check_existing",
            "relpath",
            "auto_port_ogre",  # 👈 add this
        ))

        result = export_geo.export(context, **keywords)

        if result == {'FINISHED'} and self.auto_port_ogre:
            ogre_autoport.auto_port_bz98_to_ogre(self.filepath)

        return result

        
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty


class ExportVDF(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.vdf"
    bl_label = "Export VDF"
    bl_description = "Export a Battlezone .VDF file"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".vdf"

    filter_glob: StringProperty(
        default="*.vdf",
        options={'HIDDEN'},
    )

    ExportAnimations: BoolProperty(
        name="Export Animations",
        description="Export Animations for the VDF",
        default=True,
    )

    ExportVDFOnly: BoolProperty(
        name="Export Only VDF (Don't Export GEOs)",
        description="Export only the VDF file to preserve old GEO files",
        default=False,
    )

    # NEW: Ogre auto-port checkbox
    auto_port_ogre: BoolProperty(
        name="Convert export to BZ98R Mesh/Skeleton/Material",
        description=(
            "After writing the VDF, run the Battlezone model porter to create "
            "OGRE .mesh/.skeleton/.material/.dds in the same directory"
        ),
        default=False,
    )

    def execute(self, context):
        from . import export_vdf
        from . import ogre_autoport

        # Don't pass a ton of stupid stuff to our export function. Who even cares!
        keywords = self.as_keywords(ignore=(
            "axis_forward",
            "axis_up",
            "filter_glob",
            "split_mode",
            "check_existing",
            "relpath",
            "auto_port_ogre",  # 👈 add this
        ))

        result = export_vdf.export(context, **keywords)

        if result == {'FINISHED'} and self.auto_port_ogre:
            ogre_autoport.auto_port_bz98_to_ogre(self.filepath)

        return result


        
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty


class ExportSDF(bpy.types.Operator, ExportHelper):
    """Exports a Battlezone SDF file"""
    bl_idname = "export_scene.sdf"
    bl_label = "Export SDF"
    bl_description = (
        "Export a Battlezone SDF structure file (.sdf). "
        "Note: Must have at least one animation defined in the Scene's Animation Collection "
        "for animation data to be included."
    )

    filename_ext = ".sdf"

    filter_glob: StringProperty(
        default="*.sdf",
        options={'HIDDEN'},
        maxlen=255,
    )

    ExportAnimations: BoolProperty(
        name="Export Animations",
        description="Export any animation data defined in Scene.AnimationCollection",
        default=True,
    )

    ExportSDFOnly: BoolProperty(
        name="Export SDF Only",
        description="Skip exporting referenced GEO files; export only the SDF container",
        default=False,
    )

    # NEW: Ogre auto-port toggle
    auto_port_ogre: BoolProperty(
        name="Convert export to BZ98R Mesh/Skeleton/Material",
        description=(
            "After writing the SDF, run the Battlezone model porter to create "
            "OGRE .mesh/.skeleton/.material/.dds in the same directory"
        ),
        default=False,
    )

    def execute(self, context):
        from . import export_sdf
        from . import ogre_autoport

        # Warn if there are no animation definitions in the Scene
        anims = getattr(context.scene, "AnimationCollection", None)
        if self.ExportAnimations and (not anims or len(anims) == 0):
            self.report(
                {'WARNING'},
                "No animations defined in Scene.AnimationCollection — "
                "exported SDF will contain no ANIM data."
            )

        keywords = self.as_keywords(ignore=(
            "check_existing",
            "filter_glob",
            "auto_port_ogre",   # 👈 add this
        ))

        # Do the normal SDF export
        result = export_sdf.export(context, **keywords)

        # If export succeeded and user enabled the toggle, run OGRE converter
        if result == {'FINISHED'} and self.auto_port_ogre:
            ogre_autoport.auto_port_bz98_to_ogre(self.filepath)

        return result




def menu_func_import(self, context):
    self.layout.operator(ImportGEO.bl_idname, text="Battlezone Geometry (.geo)")
    self.layout.operator(ImportVDF.bl_idname, text="Battlezone Vehicle Definition File (.vdf)")
    self.layout.operator(ImportSDF.bl_idname, text="Battlezone Structure Definition File (.sdf)")
    
def menu_func_export(self, context):
    self.layout.operator(ExportGEO.bl_idname, text="Battlezone Geometry (.geo)")
    self.layout.operator(ExportVDF.bl_idname, text="Battlezone Vehicle Definition File (.vdf)")
    self.layout.operator(ExportSDF.bl_idname, text="Battlezone Structure Definition File (.sdf)")

Properties = [
    AnimationPropertyGroup,
    GEOPropertyGroup,
    SDFVDFPropertyGroup,
    MaterialPropertyGroup,
]

GUIClasses = [
    BattlezoneGEOProperties,
    BattlezoneSDFVDFProperties,
    BattlezoneMaterialProperties,
    OPCreateNewElement,
    OPDeleteElement,
    OPGenerateCollision,
    AnimationUIList,
    AnimationPanel
]

ImportExportClasses = [
    ImportGEO,
    ImportVDF,
    ImportSDF,
    ExportGEO,
    ExportVDF,
    ExportSDF
]

def register():
    for property in Properties:
        bpy.utils.register_class(property)
 
    for guiclass in GUIClasses:
        bpy.utils.register_class(guiclass)    

    for registerclass in ImportExportClasses:
        bpy.utils.register_class(registerclass)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
    '''
    Lets register some properties for objects. This part is notably important!
    '''
    #The animations currently loaded.
    bpy.types.Scene.AnimationCollection = bpy.props.CollectionProperty(type=AnimationPropertyGroup)
    #The current animation we are viewing.
    bpy.types.Scene.CurAnimation = bpy.props.IntProperty(name="Entry")
    #Custom property groups.
    bpy.types.Material.MaterialPropertyGroup = bpy.props.PointerProperty(type=MaterialPropertyGroup)
    bpy.types.Object.GEOPropertyGroup = bpy.props.PointerProperty(type=GEOPropertyGroup)
    bpy.types.Scene.SDFVDFPropertyGroup = bpy.props.PointerProperty(type=SDFVDFPropertyGroup)

def unregister():
    for property in Properties:
        bpy.utils.unregister_class(property)

    for guiclass in GUIClasses:
        bpy.utils.unregister_class(guiclass)    

    for registerclass in ImportExportClasses:
        bpy.utils.unregister_class(registerclass)
        
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    
        #The animations currently loaded.
    bpy.types.Scene.AnimationCollection = None
    #The current animation we are viewing.
    bpy.types.Scene.CurAnimation = None
    #Custom property groups.
    bpy.types.Material.MaterialPropertyGroup = None
    bpy.types.Object.GEOPropertyGroup = None
    bpy.types.Scene.SDFVDFPropertyGroup = None

#If being tested in script editor run.
if __name__ == '__main__':
    register()
