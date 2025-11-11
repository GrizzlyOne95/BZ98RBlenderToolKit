# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

import bpy

from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        FloatVectorProperty,
        )

from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

import os

def get_default_ogre_xml_converter():
    """Try to find OgreXMLConverter.exe in the bundled ogretools folder."""
    addon_dir = os.path.dirname(__file__)
    candidate = os.path.join(addon_dir, "ogretools", "OgreXMLConverter.exe")
    if os.path.isfile(candidate):
        return candidate
    # Fallback: empty string; user can pick it manually
    return ""


if "bpy" in locals():
    import importlib


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

TERNARY_ITEMS = [
    ("AUTO", "Auto",       "Use automatic detection"),
    ("YES",  "Force Yes",  "Force enabled"),
    ("NO",   "Force No",   "Force disabled"),
]

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

# -------------------------------
# Animation Index Reference Popup
# -------------------------------

def draw_anim_index_reference_popup(self, context):
    layout = self.layout
    col = layout.column(align=False)

    col.label(text="Battlezone Animation Index Reference")
    col.separator()
    col.label(text="Indexes are per-classLabel; same index can")
    col.label(text="mean different things on different units.")
    col.separator()

    # Recycler
    col.label(text="Recycler (classLabel = recycler)")
    col.label(text="  0: Deploy")
    col.label(text="  1: Undeploy")
    col.separator()

    # Factory
    col.label(text="Factory (classLabel = factory)")
    col.label(text="  0: Deploy")
    col.label(text="  1: Undeploy")
    col.label(text="  2: Idle")
    col.label(text="  3: Deployed Idle")
    col.label(text="  4: Deployed & Ready Idle")
    col.separator()

    # Armory
    col.label(text="Armory (classLabel = armory)")
    col.label(text="  0: Launch")
    col.label(text="  1: Launch (Reverse)")
    col.separator()

    # Construction Rig
    col.label(text="ConstructionRig (classLabel = constructionrig)")
    col.label(text="  0: Deploying / Start Construction")
    col.label(text="  1: Undeploying / Finished Construction")
    col.label(text="  4: Deployed & Currently Constructing")
    col.separator()

    # Person
    col.label(text="Person (classLabel = person)")
    col.label(text="  0: Stand → Snipe")
    col.label(text="  1: Snipe → Stand")
    col.label(text="  2: Standing / Idle")
    col.label(text="  3: Sniping / Idle")
    col.label(text="  4: Walk Forwards")
    col.label(text="  5: Walk Backwards")
    col.label(text="  6: Strafe Left")
    col.label(text="  7: Strafe Right")
    col.label(text="  8: Sniped (death)")
    col.label(text="  9: idleParachute (falling from sky)")
    col.label(text="  10: landParachute (as pilot hits ground)")
    col.label(text="  11: Jump")
    col.separator()

    # Scavenger
    col.label(text="Scavenger (classLabel = scavenger)")
    col.label(text="  0: Deploy")
    col.label(text="  1: Undeploy")
    col.label(text="  2: Idle")
    col.label(text="  3: Deployed Idle")
    col.label(text="  4: Undeploy (alt)")
    col.separator()

    # Tug
    col.label(text="Tug (classLabel = tug)")
    col.label(text="  0: Deploy")
    col.label(text="  1: Undeploy")
    col.separator()

    # Howitzer
    col.label(text="Howitzer (classLabel = howitzer)")
    col.label(text="  0: Deploy")
    col.label(text="  1: Undeploy")
    col.separator()

    # TurretTank
    col.label(text="TurretTank (classLabel = turrettank)")
    col.label(text="  0: Deploy")
    col.label(text="  1: Undeploy")
    col.separator()

    # Walker
    col.label(text="Walker (classLabel = walker)")
    col.label(text="  0: Vehicle Get Out")
    col.label(text="  1: Vehicle Get In")
    col.label(text="  2: Stand / Idle (pilot inside)")
    col.label(text="  3: No Pilot / Idle")
    col.label(text="  4: Walk Forwards")
    col.label(text="  5: Walk Backwards")
    col.label(text="  6: Strafe Left")
    col.label(text="  7: Strafe Right")


class BZ_OT_ShowAnimIndexReference(bpy.types.Operator):
    """Show a quick reference for Battlezone animation indices"""
    bl_idname = "bz.show_anim_index_reference"
    bl_label = "Animation Index Reference"

    def invoke(self, context, event):
        context.window_manager.popup_menu(
            draw_anim_index_reference_popup,
            title="Animation Index Reference",
            icon='INFO'
        )
        return {'FINISHED'}


class BZ_PT_GeoTypeListPopover(bpy.types.Panel):
    bl_idname = "BZ_PT_GeoTypeListPopover"
    bl_label = "GEO Type Reference"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_ui_units_x = 220  # width of popover, tweak as you like

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=False)

        obj = context.object
        current = -1
        if obj is not None and hasattr(obj, "GEOPropertyGroup"):
            current = getattr(obj.GEOPropertyGroup, "GEOType", -1)

        col.label(text="ID – Description")
        col.separator()

        # geotypes is the global list populated by insertgeotypedata
        for idx, label, _ in geotypes:
            row = col.row()
            # Highlight the currently selected GEOType a bit
            icon = 'RADIOBUT_ON' if idx == current else 'BLANK1'
            row.label(text=label, icon=icon)

    
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
        
        box = layout.box()
        box.label(text="VDF Collision Helpers (not used for SDF)")
        box.label(text="Uses active mesh bounds to build VDF COL boxes")
        box.operator(
            "bz.generate_vdf_collision_meshes",
            text="Generate inner_col / outer_col",
        )


class BattlezoneGEOProperties(bpy.types.Panel):
    bl_idname = "OBJECT_PT_BZ_GEO"
    bl_label = "Battlezone GEO Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        geo = getattr(obj, "GEOPropertyGroup", None)
        if geo is None:
            layout.label(text="No GEO data on active object.")
            return

        # --- GEO settings box ---
        box = layout.box()
        box.label(text="SDF/VDF GEO Settings")
        box.prop(geo, "GEOType")
        box.prop(geo, "GEOFlags")

        row = box.row()
        row.popover(
            panel="BZ_PT_GeoTypeListPopover",
            text="Show GEO Types",
            icon="INFO",
        )

        # --- Collision settings box ---
        col_box = layout.box()
        col_box.label(text="GEO Collision Settings")
        col_box.prop(geo, "GenerateCollision")

        col_box.label(text="GEO Center X/Y/Z")
        split = col_box.split()
        split.prop(geo, "GeoCenterX")
        split.prop(geo, "GeoCenterY")
        split.prop(geo, "GeoCenterZ")

        col_box.label(text="Projectile Collision Box X/Y/Z")
        split = col_box.split()
        split.prop(geo, "BoxHalfHeightX")
        split.prop(geo, "BoxHalfHeightY")
        split.prop(geo, "BoxHalfHeightZ")

        col_box.prop(geo, "SphereRadius")
        col_box.operator('bz.generatecollision', text="Generate Collision Settings")

        # --- SDF-specific settings ---
        box = layout.box()
        box.label(text="SDF Specific GEO Settings")
        box.prop(geo, "SDFDDR")
        box.prop(geo, "SDFX")
        box.prop(geo, "SDFY")
        box.prop(geo, "SDFZ")
        box.prop(geo, "SDFTime")

        
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
class OPGenerateVDFCollisionMeshes(bpy.types.Operator):
    """Generate VDF-style inner_col / outer_col collision cubes from selected mesh bounds"""
    bl_idname = "bz.generate_vdf_collision_meshes"
    bl_label = "Generate VDF Collision Meshes"
    bl_description = (
        "Create inner_col and outer_col box meshes from the combined bounding box of the "
        "selected mesh objects for use as VDF collision data "
        "(SDF collision is calculated differently and does not use these)"
    )

    inner_scale: bpy.props.FloatProperty(
        name="Inner Box Scale",
        description="Scale of inner collision box relative to the visual bounds",
        default=0.7,
        min=0.0,
        max=1.0,
    )

    outer_margin: bpy.props.FloatProperty(
        name="Outer Box Margin",
        description="Extra padding added to the outer collision box (fraction of box size)",
        default=0.0,
        min=0.0,
        max=1.0,
    )

    def execute(self, context):
        import mathutils
        import bmesh

        # -----------------------------------------
        # Collect source objects
        # -----------------------------------------
        selected_meshes = [o for o in context.selected_objects if o.type == 'MESH']

        if not selected_meshes:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        # If somehow multiple selected but active is not mesh, we still proceed with selected list
        # Active is only relevant if you later want to inherit orientation, etc.

        # -----------------------------------------
        # Build a combined WORLD-space bounding box
        # -----------------------------------------
        first = True
        min_w = max_w = None

        for obj in selected_meshes:
            if not obj.bound_box:
                continue

            for corner in obj.bound_box:
                v_world = obj.matrix_world @ mathutils.Vector(corner)

                if first:
                    min_w = v_world.copy()
                    max_w = v_world.copy()
                    first = False
                else:
                    min_w.x = min(min_w.x, v_world.x)
                    min_w.y = min(min_w.y, v_world.y)
                    min_w.z = min(min_w.z, v_world.z)

                    max_w.x = max(max_w.x, v_world.x)
                    max_w.y = max(max_w.y, v_world.y)
                    max_w.z = max(max_w.z, v_world.z)

        if first or min_w is None or max_w is None:
            self.report({'ERROR'}, "Unable to compute bounding box from selected meshes")
            return {'CANCELLED'}

        center_w = (min_w + max_w) * 0.5
        half = (max_w - min_w) * 0.5

        # Avoid degenerate boxes (flat planes)
        eps = 0.01
        for attr in ("x", "y", "z"):
            if abs(getattr(half, attr)) < eps:
                setattr(half, attr, eps)

        outer_half = half * (1.0 + self.outer_margin)
        inner_half = half * self.inner_scale

        def make_box(name: str, half_vec: mathutils.Vector):
            # Reuse an existing object with that name if it's a mesh, otherwise create new
            existing = bpy.data.objects.get(name)
            if existing is not None and existing.type != 'MESH':
                existing = None

            mesh = bpy.data.meshes.new(name)

            if existing is None:
                obj_box = bpy.data.objects.new(name, mesh)
                context.collection.objects.link(obj_box)
            else:
                obj_box = existing
                obj_box.data = mesh

            bm = bmesh.new()
            # Unit cube from -1..1, centered at origin
            bmesh.ops.create_cube(bm, size=2.0)

            # Scale to the desired half-extents (still centered at origin)
            scale_mat = mathutils.Matrix.Diagonal(
                (half_vec.x, half_vec.y, half_vec.z, 1.0)
            )
            bmesh.ops.transform(bm, matrix=scale_mat, verts=bm.verts)

            bm.to_mesh(mesh)
            bm.free()

            # Place cube at the combined center in WORLD space, axis-aligned
            obj_box.matrix_world = mathutils.Matrix.Translation(center_w)

            # Helper-ish but exportable:
            obj_box.display_type = 'WIRE'
            obj_box.hide_render = True      # fine for export
            obj_box.hide_viewport = False   # must be visible so user sees them

            # No parenting – keep them in world
            obj_box.parent = None

            return obj_box

        outer_obj = make_box("outer_col", outer_half)
        inner_obj = make_box("inner_col", inner_half)

        self.report(
            {'INFO'},
            "Generated VDF inner_col and outer_col from selected mesh bounds",
        )
        return {'FINISHED'}




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

        # Animation index reference helper
        ref_box = layout.box()
        ref_box.label(text="Animation Index Reference")
        ref_box.operator(
            "bz.show_anim_index_reference",
            text="Show Animation Index Reference",
            icon='INFO'
        )


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
    bl_idname = "export_scene.geo"
    bl_label = "Export GEO"
    bl_description = "Export a Battlezone .GEO file"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".geo"

    filter_glob: StringProperty(
        default="*.geo",
        options={'HIDDEN'},
    )

    # Ogre auto-port toggle
    auto_port_ogre: BoolProperty(
        name="Create Redux Files",
        description=(
            "After writing the GEO, run the Battlezone model porter to create "
            "OGRE .mesh/.skeleton/.material/.dds in the same directory"
        ),
        default=False,
    )

    # ---------- OGRE shared options ----------

    ogre_name: StringProperty(
        name="OGRE Name (--name)",
        description="Name to give the final OGRE model files; leave blank to use the source name",
        default="",
    )

    ogre_suffix: StringProperty(
        name="Material Suffix (--suffix)",
        description="Suffix appended to material file names",
        default="_port",
    )

    ogre_flat_colors: BoolProperty(
        name="Flat Colors (--flatcolors)",
        description="Force the use of flat per-face color texturing",
        default=False,
    )

    ogre_bounds_mult: FloatVectorProperty(
        name="Bounds Scale (--boundsmult)",
        description="Scale factors for the mesh bounds (X, Y, Z)",
        size=3,
        default=(1.0, 1.0, 1.0),
        subtype='XYZ',
    )

    ogre_act_path: StringProperty(
        name="ACT Palette (--act)",
        description="Optional .act palette file for indexed .map textures",
        default="",
        #subtype='FILE_PATH',
    )

    ogre_config_path: StringProperty(
        name="Config File (--config)",
        description="Optional config file that defines default paths for the porter",
        default="",
        #subtype='FILE_PATH',
    )

    ogre_only_once: BoolProperty(
        name="Skip If Already Ported (--onlyonce)",
        description="Don't port files when the mesh is already in the target directory",
        default=False,
    )

    ogre_nowrite: BoolProperty(
        name="Dry Run: No Write (--nowrite)",
        description="Suppress file writing (for testing)",
        default=False,
    )

    ogre_dest_dir: StringProperty(
        name="Destination Directory (--dest)",
        description="Destination directory to write OGRE files into; leave blank to use export folder",
        default="",
        #subtype='DIR_PATH',
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
            "auto_port_ogre",
            "ogre_name",
            "ogre_suffix",
            "ogre_flat_colors",
            "ogre_bounds_mult",
            "ogre_act_path",
            "ogre_config_path",
            "ogre_only_once",
            "ogre_nowrite",
            "ogre_dest_dir",
        ))

        result = export_geo.export(context, **keywords)

        if result == {'FINISHED'} and self.auto_port_ogre:
            opts = {
                "name": self.ogre_name.strip() or None,
                "suffix": self.ogre_suffix.strip() or "_port",
                "flat_colors": self.ogre_flat_colors,
                "bounds_mult": list(self.ogre_bounds_mult),
                "act_path": self.ogre_act_path.strip() or None,
                "config_path": self.ogre_config_path.strip() or None,
                "only_once": self.ogre_only_once,
                "nowrite": self.ogre_nowrite,
                "dest_dir": self.ogre_dest_dir.strip() or None,
            }
            ogre_autoport.auto_port_bz98_to_ogre(self.filepath, opts)

        return result

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
        name="Create BZR Files",
        description=(
            "After writing the VDF, run the Battlezone model porter to create "
            "OGRE .mesh/.skeleton/.material/.dds in the same directory"
        ),
        default=False,
    )
    
    ogre_name: StringProperty(
        name="OGRE Name (--name)",
        description="Name to give the final OGRE model files; leave blank to use the source name",
        default="",
    )

    ogre_suffix: StringProperty(
        name="Material Suffix (--suffix)",
        description="Suffix appended to material file names",
        default="_port",
    )

    ogre_flat_colors: BoolProperty(
        name="Flat Colors (--flatcolors)",
        description="Force the use of flat per-face color texturing",
        default=False,
    )

    ogre_bounds_mult: FloatVectorProperty(
        name="Bounds Scale (--boundsmult)",
        description="Scale factors for the mesh bounds (X, Y, Z)",
        size=3,
        default=(1.0, 1.0, 1.0),
        subtype='XYZ',
    )

    ogre_act_path: StringProperty(
        name="ACT Palette (--act)",
        description="Optional .act palette file for indexed .map textures",
        default="",
        #subtype='FILE_PATH',
    )

    ogre_config_path: StringProperty(
        name="Config File (--config)",
        description="Optional config file that defines default paths for the porter",
        default="",
        #subtype='FILE_PATH',
    )

    ogre_only_once: BoolProperty(
        name="Skip If Already Ported (--onlyonce)",
        description="Don't port files when the mesh is already in the target directory",
        default=False,
    )

    ogre_nowrite: BoolProperty(
        name="Dry Run: No Write (--nowrite)",
        description="Suppress file writing (for testing)",
        default=False,
    )

    ogre_dest_dir: StringProperty(
        name="Destination Directory (--dest)",
        description="Destination directory to write OGRE files into; leave blank to use export folder",
        default="",
        #subtype='DIR_PATH',
    )
    
        # ---------- VDF-only OGRE options ----------

    ogre_headlights: BoolProperty(
        name="Headlights (--headlights)",
        description="Enable automatic creation of headlights",
        default=False,
    )

    ogre_person_mode: EnumProperty(
        name="Person Flag (--person)",
        description="Force this object to be flagged as a person",
        items=TERNARY_ITEMS,
        default="AUTO",
    )

    ogre_turret_mode: EnumProperty(
        name="Turret Flag (--turret)",
        description="Force this object to be flagged as a turret",
        items=TERNARY_ITEMS,
        default="AUTO",
    )

    ogre_cockpit_mode: EnumProperty(
        name="Cockpit Flag (--cockpit)",
        description="Force creation/suppression of separate cockpit model files",
        items=TERNARY_ITEMS,
        default="AUTO",
    )

    ogre_skeletalanims_mode: EnumProperty(
        name="Skeletal Anims (--skeletalanims)",
        description="Force creation/suppression of skeletal person animations",
        items=TERNARY_ITEMS,
        default="AUTO",
    )

    ogre_scope_mode: EnumProperty(
        name="Scope Enabled (--scope)",
        description="Force creation/suppression of a person sniper scope",
        items=TERNARY_ITEMS,
        default="AUTO",
    )

    ogre_scope_type: EnumProperty(
        name="Scope Type (--scopetype)",
        description="Sniper scope type",
        items=[
            ("AUTO",     "Auto",     "Auto choose FIXED/GEOMETRY based on scope texture"),
            ("FIXED",    "Fixed",    "Square fixed on screen (classic)"),
            ("ATTACHED", "Attached", "Square attached to the gun model"),
            ("GEOMETRY", "Geometry", "Scope textured directly on geometry"),
        ],
        default="AUTO",
    )

    ogre_scope_nation: StringProperty(
        name="Scope Nation (--scopenation)",
        description="Nation string for fixed scope placement (e.g. 'soviet')",
        default="",
    )

    ogre_scope_screen: FloatVectorProperty(
        name="Scope Screen (--scopescreen)",
        description="Camera-relative X, Y, Z, SIZE, BEHIND_DIST for fixed scope",
        size=5,
        default=(0.0, 0.0, 0.0, 1.0, 0.0),
    )

    ogre_scope_gun: StringProperty(
        name="Scope Gun (--scopegun)",
        description="Gun geo name to attach scope to (ATTACHED scope type)",
        default="",
    )

    ogre_scope_transform: FloatVectorProperty(
        name="Scope Transform (--scopetransform)",
        description="Gun-relative transform RX,RY,RZ, UX,UY,UZ, FX,FY,FZ, PX,PY,PZ",
        size=12,
        default=(1.0, 0.0, 0.0,
                 0.0, 1.0, 0.0,
                 0.0, 0.0, 1.0,
                 0.0, 0.0, 0.0),
    )

    ogre_scope_texture: StringProperty(
        name="Scope Texture (--scopetexture)",
        description="Texture name to replace with scope material (GEOMETRY scope)",
        default="__scope",
    )

    ogre_no_pov_rots: BoolProperty(
        name="No POV Rotations (--nopovrots)",
        description="Remove POV rotation keys from directional movement animations",
        default=False,
    )


    def execute(self, context):
        from . import export_vdf
        from . import ogre_autoport

        # Don't pass OGRE UI options to the VDF exporter
        keywords = self.as_keywords(ignore=(
            "axis_forward",
            "axis_up",
            "filter_glob",
            "split_mode",
            "check_existing",
            "relpath",
            "auto_port_ogre",
            "ogre_name",
            "ogre_suffix",
            "ogre_flat_colors",
            "ogre_bounds_mult",
            "ogre_act_path",
            "ogre_config_path",
            "ogre_only_once",
            "ogre_nowrite",
            "ogre_dest_dir",
            "ogre_headlights",
            "ogre_person_mode",
            "ogre_turret_mode",
            "ogre_cockpit_mode",
            "ogre_skeletalanims_mode",
            "ogre_scope_mode",
            "ogre_scope_type",
            "ogre_scope_nation",
            "ogre_scope_screen",
            "ogre_scope_gun",
            "ogre_scope_transform",
            "ogre_scope_texture",
            "ogre_no_pov_rots",
        ))

        result = export_vdf.export(context, **keywords)

        if result == {'FINISHED'} and self.auto_port_ogre:
            opts = {
                # shared
                "name": self.ogre_name.strip() or None,
                "suffix": self.ogre_suffix.strip() or "_port",
                "flat_colors": self.ogre_flat_colors,
                "bounds_mult": list(self.ogre_bounds_mult),
                "act_path": self.ogre_act_path.strip() or None,
                "config_path": self.ogre_config_path.strip() or None,
                "only_once": self.ogre_only_once,
                "nowrite": self.ogre_nowrite,
                "dest_dir": self.ogre_dest_dir.strip() or None,

                # VDF-only
                "headlights": self.ogre_headlights,
                "person_mode": self.ogre_person_mode,
                "turret_mode": self.ogre_turret_mode,
                "cockpit_mode": self.ogre_cockpit_mode,
                "skeletalanims_mode": self.ogre_skeletalanims_mode,
                "scope_mode": self.ogre_scope_mode,
                "scope_type": self.ogre_scope_type,
                "scope_nation": self.ogre_scope_nation.strip() or None,
                "scope_screen": list(self.ogre_scope_screen),
                "scope_gun": self.ogre_scope_gun.strip() or None,
                "scope_transform": list(self.ogre_scope_transform),
                "scope_texture": self.ogre_scope_texture.strip() or None,
                "no_pov_rots": self.ogre_no_pov_rots,
            }

            ogre_autoport.auto_port_bz98_to_ogre(self.filepath, opts)

        return result

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
        name="Create BZR Files",
        description=(
            "After writing the SDF, run the Battlezone model porter to create "
            "OGRE .mesh/.skeleton/.material/.dds in the same directory"
        ),
        default=False,
    )
    
    ogre_name: StringProperty(
        name="OGRE Name (--name)",
        description="Name to give the final OGRE model files; leave blank to use the source name",
        default="",
    )

    ogre_suffix: StringProperty(
        name="Material Suffix (--suffix)",
        description="Suffix appended to material file names",
        default="_port",
    )

    ogre_flat_colors: BoolProperty(
        name="Flat Colors (--flatcolors)",
        description="Force the use of flat per-face color texturing",
        default=False,
    )

    ogre_bounds_mult: FloatVectorProperty(
        name="Bounds Scale (--boundsmult)",
        description="Scale factors for the mesh bounds (X, Y, Z)",
        size=3,
        default=(1.0, 1.0, 1.0),
        subtype='XYZ',
    )

    ogre_act_path: StringProperty(
        name="ACT Palette (--act)",
        description="Optional .act palette file for indexed .map textures",
        default="",
        #subtype='FILE_PATH',
    )

    ogre_config_path: StringProperty(
        name="Config File (--config)",
        description="Optional config file that defines default paths for the porter",
        default="",
        #subtype='FILE_PATH',
    )

    ogre_only_once: BoolProperty(
        name="Skip If Already Ported (--onlyonce)",
        description="Don't port files when the mesh is already in the target directory",
        default=False,
    )

    ogre_nowrite: BoolProperty(
        name="Dry Run: No Write (--nowrite)",
        description="Suppress file writing (for testing)",
        default=False,
    )

    ogre_dest_dir: StringProperty(
        name="Destination Directory (--dest)",
        description="Destination directory to write OGRE files into; leave blank to use export folder",
        default="",
        #subtype='DIR_PATH',
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
            "axis_forward",
            "axis_up",
            "filter_glob",
            "split_mode",
            "check_existing",
            "relpath",
            "auto_port_ogre",
            "ogre_name",
            "ogre_suffix",
            "ogre_flat_colors",
            "ogre_bounds_mult",
            "ogre_act_path",
            "ogre_config_path",
            "ogre_only_once",
            "ogre_nowrite",
            "ogre_dest_dir",
        ))

        result = export_sdf.export(context, **keywords)

        if result == {'FINISHED'} and self.auto_port_ogre:
            opts = {
                "name": self.ogre_name.strip() or None,
                "suffix": self.ogre_suffix.strip() or "_port",
                "flat_colors": self.ogre_flat_colors,
                "bounds_mult": list(self.ogre_bounds_mult),
                "act_path": self.ogre_act_path.strip() or None,
                "config_path": self.ogre_config_path.strip() or None,
                "only_once": self.ogre_only_once,
                "nowrite": self.ogre_nowrite,
                "dest_dir": self.ogre_dest_dir.strip() or None,
            }
            ogre_autoport.auto_port_bz98_to_ogre(self.filepath, opts)

        return result

class BZ98TOOLS_OT_import_bzr_mesh(bpy.types.Operator, ImportHelper):
    """Import BZR Mesh (Ogre .mesh)"""
    bl_idname = "import_scene.bz98_bzr_mesh"
    bl_label = "Import Battlezone Redux Mesh (.mesh)"
    bl_options = {'UNDO'}

    filename_ext = ".mesh"
    filter_glob: StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )

    xml_converter: StringProperty(
        name="OgreXMLConverter",
        description="Path to OgreXMLConverter.exe",
        default=get_default_ogre_xml_converter(),
        # subtype='FILE_PATH',
    )

    keep_xml: BoolProperty(
        name="Keep XML files",
        description="Keep intermediate .xml files instead of deleting them",
        default=False,
    )

    import_normals: BoolProperty(
        name="Import Normals",
        default=True,
    )

    normal_mode: EnumProperty(
        name="Normal Import Mode",
        items=(
            ('custom', "Custom", "Use custom split normals if possible"),
            ('auto', "Auto", "Let Blender recompute normals"),
        ),
        default='custom',
    )

    import_shapekeys: BoolProperty(
        name="Import Shape Keys",
        default=True,
    )

    import_animations: BoolProperty(
        name="Import Animations",
        default=False,
    )

    round_frames: BoolProperty(
        name="Round Animation Frames",
        description="Round animation frames to whole frames and set scene FPS",
        default=True,
    )

    use_selected_skeleton: BoolProperty(
        name="Use Selected Armature as Skeleton",
        description="If an armature is selected, map mesh weights to it",
        default=False,
    )

    import_materials: BoolProperty(
        name="Import Materials",
        default=True,
    )

    def execute(self, context):
        # Local import to avoid circular import on addon init
        from .ogretools import OgreImport

        xml_converter = self.xml_converter or None

        return OgreImport.load(
            self,
            context,
            self.filepath,
            xml_converter=xml_converter,
            keep_xml=self.keep_xml,
            import_normals=self.import_normals,
            normal_mode=self.normal_mode,
            import_shapekeys=self.import_shapekeys,
            import_animations=self.import_animations,
            round_frames=self.round_frames,
            use_selected_skeleton=self.use_selected_skeleton,
            import_materials=self.import_materials,
        )


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "xml_converter")
        layout.prop(self, "keep_xml")
        layout.separator()
        layout.prop(self, "import_normals")
        layout.prop(self, "normal_mode")
        layout.prop(self, "import_shapekeys")
        layout.prop(self, "import_animations")
        layout.prop(self, "round_frames")
        layout.prop(self, "use_selected_skeleton")
        layout.prop(self, "import_materials")


class BZ98TOOLS_OT_export_bzr_mesh(bpy.types.Operator, ExportHelper):
    """Export BZR Mesh (Ogre .mesh + .skeleton)"""
    bl_idname = "export_scene.bz98_bzr_mesh"
    bl_label = "Export Battlezone Redux Mesh (.mesh)"
    bl_options = {'UNDO'}

    filename_ext = ".mesh"
    filter_glob: StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )

    xml_converter: StringProperty(
        name="OgreXMLConverter",
        description="Path to OgreXMLConverter.exe",
        default=get_default_ogre_xml_converter(),
        subtype='FILE_PATH',
    )

    keep_xml: BoolProperty(
        name="Keep XML files",
        description="Keep intermediate .xml instead of deleting them",
        default=False,
    )

    export_tangents: BoolProperty(
        name="Export Tangents",
        default=True,
    )

    export_binormals: BoolProperty(
        name="Export Binormals",
        default=True,
    )

    zero_tangents_binormals: BoolProperty(
        name="Zero Tangents/Binormals",
        description="Force tangents/binormals to zero (e.g. for black building meshes)",
        default=False,
    )

    export_colour: BoolProperty(
        name="Export Vertex Colours",
        default=True,
    )

    tangent_parity: BoolProperty(
        name="Export Tangent Parity",
        default=True,
    )

    apply_transform: BoolProperty(
        name="Apply Object Transforms",
        default=True,
    )

    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        default=True,
    )

    export_materials: BoolProperty(
        name="Export Materials",
        default=True,
    )

    overwrite_material: BoolProperty(
        name="Overwrite Material Files",
        default=False,
    )

    copy_textures: BoolProperty(
        name="Copy Textures Next to .mesh",
        default=False,
    )

    export_skeleton: BoolProperty(
        name="Export Skeleton",
        default=True,
    )

    export_poses: BoolProperty(
        name="Export Shape Keys as Poses",
        default=True,
    )

    export_animation: BoolProperty(
        name="Export Animations",
        default=False,
    )

    renormalize_weights: BoolProperty(
        name="Renormalize Weights",
        default=True,
    )

    batch_export: BoolProperty(
        name="Batch Export Selected Objects",
        description="Export each selected object as its own .mesh file",
        default=False,
    )

    def execute(self, context):
        # Local import to avoid circular import on addon init
        from .ogretools import OgreExport

        xml_converter = self.xml_converter or None

        return OgreExport.save(
            self,
            context,
            self.filepath,
            xml_converter=xml_converter,
            keep_xml=self.keep_xml,
            export_tangents=self.export_tangents,
            export_binormals=self.export_binormals,
            zero_tangents_binormals=self.zero_tangents_binormals,
            export_colour=self.export_colour,
            tangent_parity=self.tangent_parity,
            apply_transform=self.apply_transform,
            apply_modifiers=self.apply_modifiers,
            export_materials=self.export_materials,
            overwrite_material=self.overwrite_material,
            copy_textures=self.copy_textures,
            export_skeleton=self.export_skeleton,
            export_poses=self.export_poses,
            export_animation=self.export_animation,
            renormalize_weights=self.renormalize_weights,
            batch_export=self.batch_export,
        )


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "xml_converter")
        layout.prop(self, "keep_xml")
        layout.separator()
        col = layout.column()
        col.label(text="Geometry:")
        col.prop(self, "apply_transform")
        col.prop(self, "apply_modifiers")
        col.prop(self, "batch_export")

        layout.separator()
        col = layout.column()
        col.label(text="Tangents / Binormals:")
        col.prop(self, "export_tangents")
        col.prop(self, "export_binormals")
        col.prop(self, "zero_tangents_binormals")
        col.prop(self, "tangent_parity")

        layout.separator()
        col = layout.column()
        col.label(text="Vertex Data:")
        col.prop(self, "export_colour")

        layout.separator()
        col = layout.column()
        col.label(text="Skeleton / Animation:")
        col.prop(self, "export_skeleton")
        col.prop(self, "export_poses")
        col.prop(self, "export_animation")
        col.prop(self, "renormalize_weights")

        layout.separator()
        col = layout.column()
        col.label(text="Materials:")
        col.prop(self, "export_materials")
        col.prop(self, "overwrite_material")
        col.prop(self, "copy_textures")



def menu_func_import(self, context):
    self.layout.operator(ImportGEO.bl_idname, text="Battlezone Geometry (.geo)")
    self.layout.operator(ImportVDF.bl_idname, text="Battlezone Vehicle Definition File (.vdf)")
    self.layout.operator(ImportSDF.bl_idname, text="Battlezone Structure Definition File (.sdf)")
    self.layout.operator(BZ98TOOLS_OT_import_bzr_mesh.bl_idname, text="Battlezone 98 Redux Mesh (.mesh)")
    
def menu_func_export(self, context):
    self.layout.operator(ExportGEO.bl_idname, text="Battlezone Geometry (.geo)")
    self.layout.operator(ExportVDF.bl_idname, text="Battlezone Vehicle Definition File (.vdf)")
    self.layout.operator(ExportSDF.bl_idname, text="Battlezone Structure Definition File (.sdf)")
    self.layout.operator(BZ98TOOLS_OT_export_bzr_mesh.bl_idname, text="Battlezone 98 Redux Mesh (.mesh)")


Properties = [
    AnimationPropertyGroup,
    GEOPropertyGroup,
    SDFVDFPropertyGroup,
    MaterialPropertyGroup,
]

GUIClasses = [
    BattlezoneGEOProperties,
    BZ_PT_GeoTypeListPopover,
    BattlezoneSDFVDFProperties,
    BattlezoneMaterialProperties,
    OPCreateNewElement,
    BZ_OT_ShowAnimIndexReference,
    OPDeleteElement,
    OPGenerateCollision,
    OPGenerateVDFCollisionMeshes,
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
        
    # Register BZR Ogre mesh operators
    bpy.utils.register_class(BZ98TOOLS_OT_import_bzr_mesh)
    bpy.utils.register_class(BZ98TOOLS_OT_export_bzr_mesh)    
        
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
    # Remove menus first so UI won't try to use unregistered classes
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    # The animations currently loaded.
    bpy.types.Scene.AnimationCollection = None
    # The current animation we are viewing.
    bpy.types.Scene.CurAnimation = None
    # Custom property groups.
    bpy.types.Material.MaterialPropertyGroup = None
    bpy.types.Object.GEOPropertyGroup = None
    bpy.types.Scene.SDFVDFPropertyGroup = None

    # Unregister BZR Ogre mesh operators
    bpy.utils.unregister_class(BZ98TOOLS_OT_export_bzr_mesh)
    bpy.utils.unregister_class(BZ98TOOLS_OT_import_bzr_mesh)

    # Unregister main classes
    for registerclass in ImportExportClasses:
        bpy.utils.unregister_class(registerclass)

    for guiclass in GUIClasses:
        bpy.utils.unregister_class(guiclass)

    for property in Properties:
        bpy.utils.unregister_class(property)


#If being tested in script editor run.
if __name__ == '__main__':
    register()
