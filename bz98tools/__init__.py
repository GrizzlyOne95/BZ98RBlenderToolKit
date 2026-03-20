# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

try:
    import bpy
except ImportError:
    bpy = None

from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        FloatVectorProperty,
        CollectionProperty,
        IntProperty,
        )

from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

import os
import math
import hashlib
import json
import mathutils
import struct

from . import validation as bz_validation

ZFS_TEXTURE_EXTENSIONS = {'.map', '.pic', '.tga', '.dds', '.png', '.bmp', '.jpg', '.jpeg'}

def get_default_ogre_xml_converter():
    """Try to find OgreXMLConverter.exe in the bundled ogretools folder."""
    addon_dir = os.path.dirname(__file__)
    candidate = os.path.join(addon_dir, "ogretools", "OgreXMLConverter.exe")
    if os.path.isfile(candidate):
        return candidate
    # Fallback: empty string; user can pick it manually
    return ""


def get_default_zfs_cache_dir():
    addon_dir = os.path.dirname(__file__)
    return os.path.join(addon_dir, "_cache", "zfs")


def get_export_preset_dir(export_kind):
    addon_dir = os.path.dirname(__file__)
    return os.path.join(addon_dir, "_presets", export_kind.lower())


def get_zfs_archive_cache_dir(zfs_path, cache_root=None):
    if not zfs_path:
        return ""
    cache_root = os.path.abspath(cache_root or get_default_zfs_cache_dir())
    archive_name = os.path.splitext(os.path.basename(zfs_path))[0]
    archive_hash = hashlib.sha1(zfs_path.encode('utf-8')).hexdigest()[:8]
    return os.path.join(cache_root, f"{archive_name}_{archive_hash}")


if "bpy" in locals():
    import importlib


# ----------------------------------------------------------
#  Updated for Blender 4.5 LTS compatibility
# ----------------------------------------------------------
bl_info = {
    "name": "Battlezone GEO/VDF/SDF Formats (For Blender 4.5 LTS)",
    "description": "Import and export GEO/VDF/SDF files from Battlezone (1998 / Redux).",
    "author": "Commando950/DivisionByZero/GrizzlyOne95",
    "version": (1, 4, 0),
    "blender": (4, 5, 1),
    "category": "Import-Export",
    "wiki_url": "https://commando950.neocities.org/docs/BZBlenderAddon/"
}

TERNARY_ITEMS = [
    ("AUTO", "Auto",       "Use automatic detection"),
    ("YES",  "Force Yes",  "Force enabled"),
    ("NO",   "Force No",   "Force disabled"),
]

ANIMATION_PRESET_ITEMS = (
    ('DEPLOY_PAIR', "Deploy Pair", "Add slots 0 and 1 for common deploy/undeploy workflows"),
    ('TURRET_PAIR', "Turret Pair", "Add slots 0 and 1 for common turret motion workflows"),
    ('WALKER_CORE', "Walker Core", "Add slots 2 through 7 for a typical walker idle and movement set"),
    ('PERSON_CORE', "Person Core", "Add slots 0 through 11 for a broad person animation starter set"),
)

ANIMATION_PRESET_SLOTS = {
    'DEPLOY_PAIR': [0, 1],
    'TURRET_PAIR': [0, 1],
    'WALKER_CORE': [2, 3, 4, 5, 6, 7],
    'PERSON_CORE': list(range(0, 12)),
}

EXPORT_KIND_IDNAMES = {
    "GEO": "export_scene.geo",
    "VDF": "export_scene.vdf",
    "SDF": "export_scene.sdf",
}

EXPORT_PRESET_PROPERTY_NAMES = {
    "GEO": (
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
    ),
    "VDF": (
        "ExportAnimations",
        "ExportVDFOnly",
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
    ),
    "SDF": (
        "ExportAnimations",
        "ExportSDFOnly",
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
    ),
}

BUILTIN_EXPORT_PRESETS = {
    "GEO": (
        ("classic_geo", "Classic GEO", {
            "auto_port_ogre": False,
            "ogre_name": "",
            "ogre_suffix": "_port",
            "ogre_flat_colors": False,
            "ogre_bounds_mult": [1.0, 1.0, 1.0],
            "ogre_act_path": "",
            "ogre_config_path": "",
            "ogre_only_once": False,
            "ogre_nowrite": False,
            "ogre_dest_dir": "",
        }),
        ("geo_port", "GEO + Redux Port", {
            "auto_port_ogre": True,
            "ogre_name": "",
            "ogre_suffix": "_port",
            "ogre_flat_colors": False,
            "ogre_bounds_mult": [1.0, 1.0, 1.0],
            "ogre_act_path": "",
            "ogre_config_path": "",
            "ogre_only_once": False,
            "ogre_nowrite": False,
            "ogre_dest_dir": "",
        }),
    ),
    "VDF": (
        ("vehicle_vdf", "Vehicle VDF", {
            "ExportAnimations": True,
            "ExportVDFOnly": False,
            "auto_port_ogre": False,
            "ogre_name": "",
            "ogre_suffix": "_port",
            "ogre_flat_colors": False,
            "ogre_bounds_mult": [1.0, 1.0, 1.0],
            "ogre_act_path": "",
            "ogre_config_path": "",
            "ogre_only_once": False,
            "ogre_nowrite": False,
            "ogre_dest_dir": "",
            "ogre_headlights": False,
            "ogre_person_mode": "AUTO",
            "ogre_turret_mode": "AUTO",
            "ogre_cockpit_mode": "AUTO",
            "ogre_skeletalanims_mode": "AUTO",
            "ogre_scope_mode": "AUTO",
            "ogre_scope_type": "AUTO",
            "ogre_scope_nation": "",
            "ogre_scope_screen": [0.0, 0.0, 0.0, 1.0, 0.0],
            "ogre_scope_gun": "",
            "ogre_scope_transform": [1.0, 0.0, 0.0,
                                     0.0, 1.0, 0.0,
                                     0.0, 0.0, 1.0,
                                     0.0, 0.0, 0.0],
            "ogre_scope_texture": "__scope",
            "ogre_no_pov_rots": False,
        }),
        ("vehicle_vdf_port", "Vehicle VDF + Redux Port", {
            "ExportAnimations": True,
            "ExportVDFOnly": False,
            "auto_port_ogre": True,
            "ogre_name": "",
            "ogre_suffix": "_port",
            "ogre_flat_colors": False,
            "ogre_bounds_mult": [1.0, 1.0, 1.0],
            "ogre_act_path": "",
            "ogre_config_path": "",
            "ogre_only_once": False,
            "ogre_nowrite": False,
            "ogre_dest_dir": "",
            "ogre_headlights": False,
            "ogre_person_mode": "AUTO",
            "ogre_turret_mode": "AUTO",
            "ogre_cockpit_mode": "AUTO",
            "ogre_skeletalanims_mode": "AUTO",
            "ogre_scope_mode": "AUTO",
            "ogre_scope_type": "AUTO",
            "ogre_scope_nation": "",
            "ogre_scope_screen": [0.0, 0.0, 0.0, 1.0, 0.0],
            "ogre_scope_gun": "",
            "ogre_scope_transform": [1.0, 0.0, 0.0,
                                     0.0, 1.0, 0.0,
                                     0.0, 0.0, 1.0,
                                     0.0, 0.0, 0.0],
            "ogre_scope_texture": "__scope",
            "ogre_no_pov_rots": False,
        }),
    ),
    "SDF": (
        ("structure_sdf", "Structure SDF", {
            "ExportAnimations": True,
            "ExportSDFOnly": False,
            "auto_port_ogre": False,
            "ogre_name": "",
            "ogre_suffix": "_port",
            "ogre_flat_colors": False,
            "ogre_bounds_mult": [1.0, 1.0, 1.0],
            "ogre_act_path": "",
            "ogre_config_path": "",
            "ogre_only_once": False,
            "ogre_nowrite": False,
            "ogre_dest_dir": "",
        }),
        ("structure_sdf_port", "Structure SDF + Redux Port", {
            "ExportAnimations": True,
            "ExportSDFOnly": False,
            "auto_port_ogre": True,
            "ogre_name": "",
            "ogre_suffix": "_port",
            "ogre_flat_colors": False,
            "ogre_bounds_mult": [1.0, 1.0, 1.0],
            "ogre_act_path": "",
            "ogre_config_path": "",
            "ogre_only_once": False,
            "ogre_nowrite": False,
            "ogre_dest_dir": "",
        }),
    ),
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

    UseCustomUnknownGeoMask: bpy.props.BoolProperty(
        name="Use Custom GEO Mask",
        description="Use a custom 32-int ANIM element GEO mask instead of automatic defaults",
        default=False,
    )

    UnknownGeoMask: bpy.props.IntVectorProperty(
        name="GEO Mask",
        description="Raw 32-int ANIM element mask",
        size=32,
        default=(0,) * 32,
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

    UseAdvancedAnimHeader: bpy.props.BoolProperty(
        name="Use Advanced ANIM Header",
        description="Use custom ANIM header raw values (null2, unknown2, reserved ints)",
        default=False,
    )

    AnimNull2: bpy.props.IntProperty(
        name="ANIM null2",
        description="Raw ANIM header int at slot null2",
        default=0,
        min=-2147483648,
        max=2147483647,
    )

    AnimUnknown2: bpy.props.IntProperty(
        name="ANIM unknown2",
        description="Raw ANIM header int at slot unknown2",
        default=0,
        min=-2147483648,
        max=2147483647,
    )

    AnimReserved: bpy.props.IntVectorProperty(
        name="ANIM Reserved",
        description="Five reserved ANIM header ints",
        size=5,
        default=(0, 0, 0, 0, 0),
    )

    UseTranslation2Track: bpy.props.BoolProperty(
        name="Use Translation2 Track",
        description="Write object position keys to ANIM Translation2 instead of Position",
        default=False,
    )

    UseCustomSCPS: bpy.props.BoolProperty(
        name="Use Custom SCPS",
        description="Write custom SCPS raw ints (VDF export)",
        default=False,
    )

    SCPSData: bpy.props.IntVectorProperty(
        name="SCPS Data",
        description="Three raw SCPS ints",
        size=3,
        default=(0, 0, 0),
    )

geotypes = []
# Build default "Unknown" entries up through the supported property range.
for i in range(0, 101):
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

GEO_TYPE_ENUM_ITEMS = [
    (f"GEO_{idx}", label, label, idx)
    for idx, label, _ in geotypes
]

GEO_TYPE_UI_HINTS = {
    1: ("ERROR", "Type 1 is known to crash as a VDF/SDF GEO. Avoid using it in legacy vehicle/structure exports."),
    3: ("ERROR", "Type 3 is known to crash as a VDF/SDF GEO. Avoid using it in legacy vehicle/structure exports."),
    15: ("INFO", "Type 15 is used for spinner behavior. Spinner helpers normally export with this role."),
    38: ("INFO", "Type 38 is typically used as a Redux headlight mask helper."),
    40: ("INFO", "Type 40 is commonly used for POV / eyepoint placement."),
    70: ("INFO", "Type 70 marks a weapon hardpoint or production smoke emitter."),
    71: ("INFO", "Type 71 marks a cannon hardpoint."),
    72: ("INFO", "Type 72 marks a rocket hardpoint."),
    73: ("INFO", "Type 73 marks a mortar hardpoint."),
    74: ("INFO", "Type 74 marks a special hardpoint."),
    75: ("WARNING", "Type 75 acts as a flame emitter and usually makes the GEO geometry itself invisible."),
    76: ("INFO", "Type 76 marks a smoke emitter."),
    77: ("INFO", "Type 77 marks a dust emitter."),
}


def _get_geotype_label(geo_type_value):
    for idx, label, _ in geotypes:
        if idx == int(geo_type_value):
            return label
    return f"{int(geo_type_value)} - Unknown"


def _get_geotype_enum_value(self):
    value = int(getattr(self, "GEOType", 60))
    if value < 0:
        return 0
    if value > 100:
        return 100
    return value


def _set_geotype_enum_value(self, value):
    self["GEOType"] = int(value)


def _draw_geotype_hint(layout, geo_type_value):
    hint = GEO_TYPE_UI_HINTS.get(int(geo_type_value))
    if hint is None:
        return

    severity, message = hint
    box = layout.box()
    if severity == "ERROR":
        icon = 'ERROR'
    elif severity == "WARNING":
        icon = 'WARNING'
    else:
        icon = 'INFO'
    box.label(text=message, icon=icon)

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

    GEOTypeEnum: bpy.props.EnumProperty(
        name="GEO Type",
        description="Named GEO type selector for common Battlezone roles",
        items=GEO_TYPE_ENUM_ITEMS,
        get=_get_geotype_enum_value,
        set=_set_geotype_enum_value,
    )
    
    GEOFlags: bpy.props.IntProperty(
        name="GEO Flags",
        description="Bitfield of GEO flags (32-bit). Each bit enables a specific Battlezone GEO behavior.",
        default=0,
        min=-2147483648,
        max=2147483647,
    )

    IsSpinnerHelper: bpy.props.BoolProperty(
        name="Spinner Helper",
        description="Treat this GEO as a spinner controller helper for VDF export",
        default=False,
    )

    SpinnerTarget: bpy.props.StringProperty(
        name="Spinner Target",
        description="Object name this spinner helper should be written after in VDF",
        default="",
        maxlen=64,
    )

    SpinnerAxis: bpy.props.FloatVectorProperty(
        name="Spinner Axis",
        description="Spinner axis vector in VDF coordinates; direction = axis, magnitude = radians/sec when speed is 1",
        size=3,
        default=(1.0, 0.0, 0.0),
    )

    SpinnerSpeed: bpy.props.FloatProperty(
        name="Spinner Speed",
        description="Multiplier applied to Spinner Axis when exporting",
        default=1.0,
        min=-100000.0,
        max=100000.0,
    )

    UseRawVDFMatrix: bpy.props.BoolProperty(
        name="Use Raw VDF Matrix",
        description="Write the raw 12-float VDF transform matrix directly instead of using Blender transform decomposition",
        default=False,
    )

    RawVDFMatrix: bpy.props.FloatVectorProperty(
        name="Raw VDF Matrix",
        description="12 floats in order: right_x right_y right_z, up_x up_y up_z, front_x front_y front_z, pos_x pos_y pos_z",
        size=12,
        default=(
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
            0.0, 0.0, 0.0,
        ),
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

    GEOHeaderUnknown: bpy.props.IntProperty(
        name="GEO Header Unknown1",
        description="Raw GEO header int (historically 69)",
        default=69,
        min=-2147483648,
        max=2147483647,
    )

    GEOHeaderUnknown2: bpy.props.IntProperty(
        name="GEO Header Unknown2",
        description="Raw GEO header trailing int",
        default=0,
        min=-2147483648,
        max=2147483647,
    )

    GEOFaceUnknownDefault: bpy.props.IntProperty(
        name="Face Unknown Raw",
        description="Default raw face int field used when per-face attributes are missing",
        default=0,
        min=-2147483648,
        max=2147483647,
    )

    GEOFaceShadeTypeDefault: bpy.props.IntProperty(
        name="Face Shade Type",
        description="Default face shade type byte (see GEO editor references)",
        default=4,
        min=0,
        max=255,
    )

    GEOFaceTextureTypeDefault: bpy.props.IntProperty(
        name="Face Texture Type",
        description="Default face texture flags byte",
        default=0,
        min=0,
        max=255,
    )

    GEOFaceXluscentTypeDefault: bpy.props.IntProperty(
        name="Face Xluscent Type",
        description="Default face translucency byte",
        default=0,
        min=0,
        max=255,
    )

    GEOFaceParentDefault: bpy.props.IntProperty(
        name="Face Parent",
        description="Default face parent index when per-face attributes are missing",
        default=0,
        min=-2147483648,
        max=2147483647,
    )

    GEOFaceNodeDefault: bpy.props.IntProperty(
        name="Face Node",
        description="Default face node/tree-branch int when per-face attributes are missing",
        default=0,
        min=-2147483648,
        max=2147483647,
    )

class MaterialPropertyGroup(bpy.types.PropertyGroup):
    MapTexture: bpy.props.StringProperty(
        name="Texture",
        description="The name of the .map texture that this material will represent. Do not include .map extension name.",
        default = '',
        maxlen=8
    )


class ValidationIssuePropertyGroup(bpy.types.PropertyGroup):
    severity: bpy.props.StringProperty(name="Severity")
    scope: bpy.props.StringProperty(name="Scope")
    target: bpy.props.StringProperty(name="Target")
    message: bpy.props.StringProperty(name="Message")
    export_modes: bpy.props.StringProperty(name="Export Modes")
    object_name: bpy.props.StringProperty(name="Object Name")
    action: bpy.props.StringProperty(name="Action")


def _store_validation_results(scene, issues):
    scene.bz_validation_issues.clear()
    for issue in issues:
        item = scene.bz_validation_issues.add()
        item.severity = issue["severity"]
        item.scope = issue.get("scope", "")
        item.target = issue.get("target", "")
        item.message = issue["message"]
        item.export_modes = ",".join(sorted(issue.get("export_modes", {"ALL"})))
        item.object_name = issue.get("object_name", "")
        item.action = issue.get("action", "")
    scene.bz_validation_signature = _compute_validation_signature(scene)


def _compute_validation_signature(scene):
    digest = hashlib.sha1()
    objects = sorted(getattr(scene, "objects", []), key=lambda obj: obj.name.lower())

    for obj in objects:
        parent_name = getattr(getattr(obj, "parent", None), "name", "")
        geo_props = getattr(obj, "GEOPropertyGroup", None)
        digest.update(
            (
                f"OBJ|{obj.name}|{getattr(obj, 'type', '')}|{parent_name}|"
                f"{int(getattr(geo_props, 'GEOType', 0))}|"
                f"{int(bool(getattr(geo_props, 'IsSpinnerHelper', False)))}|"
                f"{len(getattr(getattr(obj, 'data', None), 'vertices', []))}\n"
            ).encode("utf-8", errors="ignore")
        )

        mesh = getattr(obj, "data", None)
        materials = getattr(mesh, "materials", None) or []
        for slot_index, material in enumerate(materials):
            if material is None:
                digest.update(f"MAT|{obj.name}|{slot_index}|<empty>\n".encode("utf-8"))
                continue

            mat_props = getattr(material, "MaterialPropertyGroup", None)
            texture_name = (getattr(mat_props, "MapTexture", "") or "").strip() if mat_props else ""
            digest.update(
                (
                    f"MAT|{obj.name}|{slot_index}|{material.name}|{texture_name}|"
                    f"{getattr(material, 'diffuse_color', ())}\n"
                ).encode("utf-8", errors="ignore")
            )

    return digest.hexdigest()


def _validation_results_are_stale(scene):
    stored_signature = getattr(scene, "bz_validation_signature", "") or ""
    if not stored_signature:
        return len(getattr(scene, "bz_validation_issues", [])) > 0
    return stored_signature != _compute_validation_signature(scene)


def _get_validation_counts(scene, export_mode="ALL"):
    counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for item in getattr(scene, "bz_validation_issues", []):
        export_modes = {
            part.strip()
            for part in (item.export_modes or "ALL").split(",")
            if part.strip()
        }
        if "ALL" not in export_modes and export_mode not in export_modes:
            continue
        counts[item.severity] = counts.get(item.severity, 0) + 1
    return counts


def _draw_validation_summary_box(layout, scene, export_mode="ALL"):
    box = layout.box()
    box.label(text="Validation", icon='CHECKMARK')
    box.operator("bz.validate_scene", text="Validate Battlezone Scene", icon='VIEWZOOM')

    issues = getattr(scene, "bz_validation_issues", None)
    if issues is None or len(issues) == 0:
        box.label(text="No validation results yet.", icon='INFO')
        return box

    counts = _get_validation_counts(scene, export_mode=export_mode)
    row = box.row(align=True)
    row.label(text=f"Errors: {counts['ERROR']}")
    row.label(text=f"Warnings: {counts['WARNING']}")
    row.label(text=f"Info: {counts['INFO']}")
    if _validation_results_are_stale(scene):
        box.label(text="Results may be stale after scene changes.", icon='ERROR')
    return box


def _draw_shared_autoport_options(layout, operator):
    layout.prop(operator, "ogre_name")
    layout.prop(operator, "ogre_suffix")
    layout.prop(operator, "ogre_flat_colors")
    layout.prop(operator, "ogre_bounds_mult")
    layout.prop(operator, "ogre_act_path")
    layout.prop(operator, "ogre_config_path")
    layout.prop(operator, "ogre_dest_dir")

    adv = layout.box()
    adv.label(text="Advanced")
    adv.prop(operator, "ogre_only_once")
    adv.prop(operator, "ogre_nowrite")


def _draw_vdf_autoport_options(layout, operator):
    box = layout.box()
    box.label(text="VDF-Specific BZR Options")
    box.prop(operator, "ogre_headlights")
    box.prop(operator, "ogre_person_mode")
    box.prop(operator, "ogre_turret_mode")
    box.prop(operator, "ogre_cockpit_mode")
    box.prop(operator, "ogre_skeletalanims_mode")
    box.prop(operator, "ogre_scope_mode")
    box.prop(operator, "ogre_scope_type")
    box.prop(operator, "ogre_scope_nation")
    box.prop(operator, "ogre_scope_screen")
    box.prop(operator, "ogre_scope_gun")
    box.prop(operator, "ogre_scope_transform")
    box.prop(operator, "ogre_scope_texture")
    box.prop(operator, "ogre_no_pov_rots")


def _draw_xyz_row(layout, prop_group, prop_names, labels):
    row = layout.row(align=True)
    for prop_name, label in zip(prop_names, labels):
        row.prop(prop_group, prop_name, text=label)


def _derive_legacy_texture_name(name):
    derived = os.path.splitext((name or "").strip())[0].replace(" ", "_").lower()
    return derived[:8]


def _get_material_image_name(material):
    node_tree = getattr(material, "node_tree", None)
    if node_tree is None:
        return ""

    image_nodes = [
        node for node in getattr(node_tree, "nodes", [])
        if getattr(node, "type", "") == 'TEX_IMAGE' and getattr(node, "image", None) is not None
    ]
    if not image_nodes:
        return ""

    active_node = next((node for node in image_nodes if getattr(node, "select", False)), None)
    if active_node is None:
        active_node = image_nodes[0]

    image = active_node.image
    return _derive_legacy_texture_name(getattr(image, "name", "") or getattr(image, "filepath", ""))


def _get_material_texture_preview(material):
    material_props = getattr(material, "MaterialPropertyGroup", None)
    explicit_name = ""
    if material_props is not None:
        explicit_name = (getattr(material_props, "MapTexture", "") or "").strip()

    image_name = _get_material_image_name(material)
    derived_name = _derive_legacy_texture_name(getattr(material, "name", ""))
    resolved_name = explicit_name or image_name or derived_name

    if explicit_name:
        source = "explicit"
    elif image_name:
        source = "image"
    elif derived_name:
        source = "derived"
    else:
        source = "missing"

    return explicit_name, image_name, derived_name, resolved_name, source


def _get_animation_index_hint(index_value):
    index_value = int(index_value)
    if index_value == 0:
        return "Slot 0 is commonly the primary action: deploy, launch, get-out, or stance change depending on classLabel."
    if index_value == 1:
        return "Slot 1 is commonly the reverse action: undeploy, return, get-in, or reverse stance change."
    if index_value == 2:
        return "Slot 2 is often an idle or standing idle state on units that support multiple animation slots."
    if index_value == 3:
        return "Slot 3 is often a deployed idle or alternate idle state."
    if index_value == 4:
        return "Slot 4 is often an active deployed state or forward movement on walkers/persons."
    if index_value in (5, 6, 7):
        return "Slots 5-7 are commonly movement directions on walkers and person units."
    if index_value in (8, 9, 10, 11):
        return "Slots 8-11 are commonly situational character animations such as death, parachute, or jump states."
    return "Animation index meaning is classLabel-dependent. Use the reference popup to confirm the slot for this unit type."


def _copy_animation_item(source_item, dest_item):
    dest_item.Index = source_item.Index
    dest_item.Start = source_item.Start
    dest_item.Length = source_item.Length
    dest_item.Loop = source_item.Loop
    dest_item.Speed = source_item.Speed
    dest_item.UseCustomUnknownGeoMask = source_item.UseCustomUnknownGeoMask
    dest_item.UnknownGeoMask = tuple(source_item.UnknownGeoMask)


def _get_active_export_operator(context, export_kind):
    expected_idname = EXPORT_KIND_IDNAMES.get(export_kind)
    space = getattr(context, "space_data", None)
    operator = getattr(space, "active_operator", None) if space is not None else None
    if operator is None:
        return None
    if getattr(operator, "bl_idname", "") != expected_idname:
        return None
    return operator


def _normalize_preset_filename(name):
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in (name or "").strip())
    cleaned = cleaned.strip("._")
    return cleaned or "preset"


def _serialize_export_operator(operator, export_kind):
    values = {}
    for prop_name in EXPORT_PRESET_PROPERTY_NAMES.get(export_kind, ()):
        if not hasattr(operator, prop_name):
            continue
        value = getattr(operator, prop_name)
        if isinstance(value, (list, tuple)):
            values[prop_name] = list(value)
        else:
            values[prop_name] = value
    return values


def _apply_export_preset_values(operator, export_kind, values):
    for prop_name in EXPORT_PRESET_PROPERTY_NAMES.get(export_kind, ()):
        if prop_name not in values or not hasattr(operator, prop_name):
            continue
        value = values[prop_name]
        current = getattr(operator, prop_name)
        if isinstance(current, (list, tuple)):
            setattr(operator, prop_name, tuple(value))
        else:
            setattr(operator, prop_name, value)


def _get_builtin_export_preset(export_kind, preset_key):
    for key, _label, values in BUILTIN_EXPORT_PRESETS.get(export_kind, ()):
        if key == preset_key:
            return values
    return None


def _list_custom_export_presets(export_kind):
    preset_dir = get_export_preset_dir(export_kind)
    if not os.path.isdir(preset_dir):
        return []

    results = []
    for entry in sorted(os.listdir(preset_dir)):
        if not entry.lower().endswith(".json"):
            continue
        path = os.path.join(preset_dir, entry)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        label = (payload.get("label") or os.path.splitext(entry)[0]).strip()
        results.append({
            "label": label,
            "path": path,
        })
    return results


def _load_custom_export_preset(export_kind, preset_label):
    for entry in _list_custom_export_presets(export_kind):
        if entry["label"] != preset_label:
            continue
        try:
            with open(entry["path"], "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError, json.JSONDecodeError):
            return None
        return payload.get("values", {})
    return None


def _draw_export_preset_box(layout, export_kind):
    box = layout.box()
    box.label(text="Presets")
    if export_kind == "GEO":
        box.menu("BZ98TOOLS_MT_geo_export_presets", text="Apply Preset")
        box.menu("BZ98TOOLS_MT_geo_delete_export_preset", text="Delete Saved Preset")
    elif export_kind == "VDF":
        box.menu("BZ98TOOLS_MT_vdf_export_presets", text="Apply Preset")
        box.menu("BZ98TOOLS_MT_vdf_delete_export_preset", text="Delete Saved Preset")
    else:
        box.menu("BZ98TOOLS_MT_sdf_export_presets", text="Apply Preset")
        box.menu("BZ98TOOLS_MT_sdf_delete_export_preset", text="Delete Saved Preset")

    save_op = box.operator("bz.save_export_preset", text="Save Current Settings")
    save_op.export_kind = export_kind
    return box


def _draw_export_preset_menu_entries(layout, export_kind, delete_mode=False):
    if not delete_mode:
        for preset_key, label, _values in BUILTIN_EXPORT_PRESETS.get(export_kind, ()):
            op = layout.operator("bz.apply_export_preset", text=label, icon='IMPORT')
            op.export_kind = export_kind
            op.preset_key = preset_key
            op.custom_label = ""

        custom_presets = _list_custom_export_presets(export_kind)
        if custom_presets:
            layout.separator()
            layout.label(text="Saved Presets")
            for entry in custom_presets:
                op = layout.operator("bz.apply_export_preset", text=entry["label"], icon='FILE')
                op.export_kind = export_kind
                op.preset_key = ""
                op.custom_label = entry["label"]
        else:
            layout.separator()
            layout.label(text="No saved presets yet.", icon='INFO')
        return

    custom_presets = _list_custom_export_presets(export_kind)
    if not custom_presets:
        layout.label(text="No saved presets yet.", icon='INFO')
        return

    for entry in custom_presets:
        op = layout.operator("bz.delete_export_preset", text=entry["label"], icon='TRASH')
        op.export_kind = export_kind
        op.custom_label = entry["label"]

'''
PANEL DEFINITIONS
BattlezoneSDFVDFProperties - Stores all the properties of the current SDF/VDF in the scene tab.
BattlezoneGEOProperties - Stores all the properties of a GEO object in the object tab of objects.
'''
class BattlezoneSDFVDFProperties(bpy.types.Panel):
    bl_idname = "SCENE_PT_BZ_SDFVDF"
    bl_label = "Battlezone"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        SDFVDFPropertyGroup = scene.SDFVDFPropertyGroup

        layout.prop(SDFVDFPropertyGroup, "Name", text="Internal Name")
        row = layout.row(align=True)
        row.label(text=f"Animation Elements: {len(scene.AnimationCollection)}", icon='ANIM')
        row.label(text=f"Validation Issues: {len(getattr(scene, 'bz_validation_issues', []))}", icon='CHECKMARK')


class BZ98TOOLS_PT_scene_asset_properties(bpy.types.Panel):
    bl_idname = "SCENE_PT_BZ_ASSET_PROPERTIES"
    bl_label = "Asset Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "SCENE_PT_BZ_SDFVDF"

    def draw(self, context):
        layout = self.layout
        props = context.scene.SDFVDFPropertyGroup

        vdf_box = layout.box()
        vdf_box.label(text="VDF Settings")
        vdf_box.prop(props, "VehicleSize")
        vdf_box.prop(props, "VehicleType")
        vdf_box.prop(props, "Mass")
        vdf_box.prop(props, "CollMult", text="Collision Multiplier")
        vdf_box.prop(props, "DragCoefficient")

        sdf_box = layout.box()
        sdf_box.label(text="SDF Settings")
        sdf_box.prop(props, "StructureType")
        sdf_box.prop(props, "Defensive")
        sdf_box.prop(props, "DeathExplosion", text="Death Explosion")
        sdf_box.prop(props, "DeathSound", text="Death Sound")

        lod_box = layout.box()
        lod_box.label(text="Level of Detail")
        lod_box.prop(props, "LOD1")
        lod_box.prop(props, "LOD2")
        lod_box.prop(props, "LOD3")
        lod_box.prop(props, "LOD4")
        lod_box.prop(props, "LOD5")


class BZ98TOOLS_PT_scene_collision_helpers(bpy.types.Panel):
    bl_idname = "SCENE_PT_BZ_COLLISION_HELPERS"
    bl_label = "Collision Helpers"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "SCENE_PT_BZ_SDFVDF"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="VDF Collision Helpers")
        box.label(text="For vehicles only. SDF collision is stored per GEO.")
        box.label(text="Uses selected mesh bounds to build inner_col and outer_col.")
        box.operator(
            "bz.generate_vdf_collision_meshes",
            text="Generate inner_col / outer_col",
        )


class BZ98TOOLS_PT_scene_advanced(bpy.types.Panel):
    bl_idname = "SCENE_PT_BZ_ADVANCED"
    bl_label = "Advanced"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "SCENE_PT_BZ_SDFVDF"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.SDFVDFPropertyGroup

        anim_box = layout.box()
        anim_box.label(text="ANIM Header / Track Overrides")
        anim_box.prop(props, "UseAdvancedAnimHeader")
        if props.UseAdvancedAnimHeader:
            anim_box.prop(props, "AnimNull2")
            anim_box.prop(props, "AnimUnknown2")
            anim_box.prop(props, "AnimReserved")
        anim_box.prop(props, "UseTranslation2Track")

        scps_box = layout.box()
        scps_box.label(text="VDF SCPS Raw")
        scps_box.prop(props, "UseCustomSCPS")
        if props.UseCustomSCPS:
            scps_box.prop(props, "SCPSData")


class BZ98TOOLS_OT_validate_scene(bpy.types.Operator):
    """Validate scene objects for legacy Battlezone export"""
    bl_idname = "bz.validate_scene"
    bl_label = "Validate Battlezone Scene"

    def execute(self, context):
        issues = bz_validation.collect_legacy_validation_issues(context, export_mode="ALL")
        _store_validation_results(context.scene, issues)

        counts = _get_validation_counts(context.scene, export_mode="ALL")
        if counts["ERROR"] > 0:
            self.report(
                {'WARNING'},
                f"Validation found {counts['ERROR']} errors, {counts['WARNING']} warnings, and {counts['INFO']} info items.",
            )
        elif counts["WARNING"] > 0 or counts["INFO"] > 0:
            self.report(
                {'INFO'},
                f"Validation found {counts['WARNING']} warnings and {counts['INFO']} info items.",
            )
        else:
            self.report({'INFO'}, "Validation found no legacy export issues.")
        return {'FINISHED'}


class BZ98TOOLS_OT_select_validation_target(bpy.types.Operator):
    bl_idname = "bz.select_validation_target"
    bl_label = "Select Validation Target"
    bl_description = "Select and activate the object referenced by this validation issue"

    object_name: StringProperty(name="Object Name", default="")

    def execute(self, context):
        if not self.object_name:
            self.report({'ERROR'}, "Validation issue has no selectable object.")
            return {'CANCELLED'}

        obj = context.scene.objects.get(self.object_name)
        if obj is None:
            self.report({'ERROR'}, f"Could not find object '{self.object_name}'.")
            return {'CANCELLED'}

        for selected in list(context.selected_objects):
            selected.select_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj
        self.report({'INFO'}, f"Selected '{obj.name}'.")
        return {'FINISHED'}


class BZ98TOOLS_OT_fix_validation_name(bpy.types.Operator):
    bl_idname = "bz.fix_validation_name"
    bl_label = "Fix Legacy Name"
    bl_description = "Rename this object to a valid legacy Battlezone export name"

    object_name: StringProperty(name="Object Name", default="")

    def execute(self, context):
        if not self.object_name:
            self.report({'ERROR'}, "Validation issue has no rename target.")
            return {'CANCELLED'}

        obj = context.scene.objects.get(self.object_name)
        if obj is None:
            self.report({'ERROR'}, f"Could not find object '{self.object_name}'.")
            return {'CANCELLED'}

        original_name = obj.name
        source_name = "".join(
            ch for ch in original_name.lower().replace(" ", "_")
            if ch.isalnum() or ch == "_"
        )
        if not source_name:
            source_name = "geo"

        lod = 3
        if len(original_name) >= 4 and original_name[3] in {'1', '2', '3'}:
            lod = int(original_name[3])

        min_len = max(5, min(8, len(source_name)))
        chars = list(source_name[:8].ljust(min_len, 'x'))
        chars[3] = str(lod)
        chars[4] = '1'
        candidate = "".join(chars[:8])

        existing = {
            scene_obj.name.lower()
            for scene_obj in context.scene.objects
            if scene_obj != obj
        }
        if candidate.lower() in existing:
            base = candidate[:7]
            for suffix in "0123456789abcdefghijklmnopqrstuvwxyz":
                alt = (base + suffix)[:8]
                if alt.lower() not in existing:
                    candidate = alt
                    break

        obj.name = candidate
        self.report({'INFO'}, f"Renamed '{original_name}' to '{candidate}'.")
        return {'FINISHED'}


class BZ98TOOLS_PT_validation(bpy.types.Panel):
    bl_idname = "SCENE_PT_BZ_VALIDATION"
    bl_label = "Battlezone Export Validation"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "SCENE_PT_BZ_SDFVDF"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        _draw_validation_summary_box(layout, scene, export_mode="ALL")

        issues = getattr(scene, "bz_validation_issues", None)
        if issues is None or len(issues) == 0:
            return

        list_box = layout.box()
        list_box.label(text="Latest Results")
        if _validation_results_are_stale(scene):
            list_box.label(text="Scene data changed after the last validation run.", icon='ERROR')
        shown = 0
        for item in issues:
            if shown >= 20:
                list_box.label(text="More results are available after the first 20 entries.")
                break

            if item.severity == "ERROR":
                icon = 'ERROR'
            elif item.severity == "WARNING":
                icon = 'WARNING'
            else:
                icon = 'INFO'

            row = list_box.row()
            label = f"{item.scope}"
            if item.target:
                label += f": {item.target}"
            row.label(text=label, icon=icon)
            if item.object_name:
                op = row.operator("bz.select_validation_target", text="Select", icon='RESTRICT_SELECT_OFF')
                op.object_name = item.object_name
            if item.action == "fix_name" and item.object_name:
                op = row.operator("bz.fix_validation_name", text="Fix Name", icon='SORTALPHA')
                op.object_name = item.object_name

            msg_row = list_box.row()
            msg_row.scale_y = 0.85
            msg_row.label(text=item.message)
            shown += 1


class BattlezoneGEOProperties(bpy.types.Panel):
    bl_idname = "OBJECT_PT_BZ_GEO"
    bl_label = "Battlezone GEO"
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

        layout.prop(geo, "GEOTypeEnum", text="GEO Type")
        layout.prop(geo, "GEOFlags")

        row = layout.row()
        row.popover(
            panel="BZ_PT_GeoTypeListPopover",
            text="Show GEO Types",
            icon="INFO",
        )
        layout.label(text=f"Selected Role: {_get_geotype_label(geo.GEOType)}")
        _draw_geotype_hint(layout, geo.GEOType)
        if getattr(obj, "type", None) == 'MESH':
            layout.label(text=f"Vertices: {len(obj.data.vertices)}", icon='MESH_DATA')
        else:
            layout.label(text="Non-mesh object. Advanced helper workflow only.", icon='INFO')


class BZ98TOOLS_PT_geo_collision(bpy.types.Panel):
    bl_idname = "OBJECT_PT_BZ_GEO_COLLISION"
    bl_label = "Collision"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "OBJECT_PT_BZ_GEO"

    def draw(self, context):
        layout = self.layout
        geo = getattr(context.object, "GEOPropertyGroup", None)
        if geo is None:
            layout.label(text="No GEO data on active object.")
            return

        layout.prop(geo, "GenerateCollision")
        layout.label(text="GEO Center")
        _draw_xyz_row(layout, geo, ("GeoCenterX", "GeoCenterY", "GeoCenterZ"), ("X", "Y", "Z"))
        layout.label(text="Projectile Box Half-Extents")
        _draw_xyz_row(layout, geo, ("BoxHalfHeightX", "BoxHalfHeightY", "BoxHalfHeightZ"), ("X", "Y", "Z"))
        layout.prop(geo, "SphereRadius")
        layout.operator('bz.generatecollision', text="Generate Collision Settings")


class BZ98TOOLS_PT_geo_sdf(bpy.types.Panel):
    bl_idname = "OBJECT_PT_BZ_GEO_SDF"
    bl_label = "SDF Extras"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "OBJECT_PT_BZ_GEO"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        geo = getattr(context.object, "GEOPropertyGroup", None)
        if geo is None:
            layout.label(text="No GEO data on active object.")
            return

        layout.prop(geo, "SDFDDR")
        _draw_xyz_row(layout, geo, ("SDFX", "SDFY", "SDFZ"), ("X", "Y", "Z"))
        layout.prop(geo, "SDFTime")


class BZ98TOOLS_PT_geo_vdf(bpy.types.Panel):
    bl_idname = "OBJECT_PT_BZ_GEO_VDF"
    bl_label = "VDF Extras"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "OBJECT_PT_BZ_GEO"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        geo = getattr(context.object, "GEOPropertyGroup", None)
        if geo is None:
            layout.label(text="No GEO data on active object.")
            return

        layout.operator("bz.create_spinner_helper", text="Create Spinner Helper")
        layout.prop(geo, "IsSpinnerHelper")
        if geo.IsSpinnerHelper:
            layout.prop(geo, "SpinnerTarget")
            layout.prop(geo, "SpinnerAxis")
            layout.prop(geo, "SpinnerSpeed")
            layout.label(text="Spinner helpers export as GEO Type 15.", icon='INFO')


class BZ98TOOLS_PT_geo_advanced(bpy.types.Panel):
    bl_idname = "OBJECT_PT_BZ_GEO_ADVANCED"
    bl_label = "Experimental"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "OBJECT_PT_BZ_GEO"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        geo = getattr(context.object, "GEOPropertyGroup", None)
        if geo is None:
            layout.label(text="No GEO data on active object.")
            return

        raw_box = layout.box()
        raw_box.label(text="VDF Transform Override")
        raw_box.prop(geo, "UseRawVDFMatrix")
        raw_box.operator("bz.capture_raw_vdf_matrix", text="Capture From Current Transform")
        if geo.UseRawVDFMatrix:
            raw_box.label(text="Order: right, up, front, position")
            raw_box.prop(geo, "RawVDFMatrix")

        face_box = layout.box()
        face_box.label(text="GEO Header / Face Raw")
        face_box.prop(geo, "GEOHeaderUnknown")
        face_box.prop(geo, "GEOHeaderUnknown2")
        face_box.prop(geo, "GEOFaceUnknownDefault")
        face_box.prop(geo, "GEOFaceShadeTypeDefault")
        face_box.prop(geo, "GEOFaceTextureTypeDefault")
        face_box.prop(geo, "GEOFaceXluscentTypeDefault")
        face_box.prop(geo, "GEOFaceParentDefault")
        face_box.prop(geo, "GEOFaceNodeDefault")
        face_box.label(text="Per-face attrs: bz_face_* (Spreadsheet).")

        
class BZ98TOOLS_OT_fill_material_texture_name(bpy.types.Operator):
    bl_idname = "bz.fill_material_texture_name"
    bl_label = "Use Material Name"
    bl_description = "Fill the Battlezone texture name from the current Blender material name"

    def execute(self, context):
        material = context.material
        if material is None:
            self.report({'ERROR'}, "No active material.")
            return {'CANCELLED'}

        material_props = getattr(material, "MaterialPropertyGroup", None)
        if material_props is None:
            self.report({'ERROR'}, "Active material has no Battlezone material properties.")
            return {'CANCELLED'}

        derived_name = _derive_legacy_texture_name(material.name)
        if not derived_name:
            self.report({'ERROR'}, "Material name cannot be converted into a Battlezone texture name.")
            return {'CANCELLED'}

        material_props.MapTexture = derived_name
        self.report({'INFO'}, f"Battlezone texture name set to '{derived_name}'.")
        return {'FINISHED'}


class BZ98TOOLS_OT_fill_material_texture_from_image(bpy.types.Operator):
    bl_idname = "bz.fill_material_texture_from_image"
    bl_label = "Use Image Name"
    bl_description = "Fill the Battlezone texture name from the linked image texture"

    def execute(self, context):
        material = context.material
        if material is None:
            self.report({'ERROR'}, "No active material.")
            return {'CANCELLED'}

        material_props = getattr(material, "MaterialPropertyGroup", None)
        if material_props is None:
            self.report({'ERROR'}, "Active material has no Battlezone material properties.")
            return {'CANCELLED'}

        derived_name = _get_material_image_name(material)
        if not derived_name:
            self.report({'ERROR'}, "No linked image texture was found on this material.")
            return {'CANCELLED'}

        material_props.MapTexture = derived_name
        self.report({'INFO'}, f"Battlezone texture name set to '{derived_name}' from the linked image.")
        return {'FINISHED'}


class BattlezoneMaterialProperties(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_BZ_GEO"
    bl_label = "Battlezone Material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        material = context.material
        MaterialPropertyGroup = material.MaterialPropertyGroup

        explicit_name, image_name, derived_name, resolved_name, source = _get_material_texture_preview(material)

        box = layout.box()
        box.label(text="Legacy Texture")
        box.prop(MaterialPropertyGroup, "MapTexture", text="Texture Name")

        row = box.row(align=True)
        row.operator("bz.fill_material_texture_name", text="Use Material Name")
        image_row = row.row(align=True)
        image_row.enabled = bool(image_name)
        image_row.operator("bz.fill_material_texture_from_image", text="Use Image Name")

        preview_box = layout.box()
        preview_box.label(text="Export Preview")
        preview_box.label(text=f"Resolved Name: {resolved_name or '(none)'}")
        preview_box.label(text=f"Source: {source}")
        if explicit_name and len(explicit_name) > 8:
            preview_box.label(text="Explicit Battlezone texture names should stay within 8 characters.", icon='WARNING')
        elif image_name and not explicit_name:
            preview_box.label(text=f"If left blank, export will derive '{image_name}' from the linked image.", icon='INFO')
        elif not explicit_name and derived_name:
            preview_box.label(text=f"If left blank, export will derive '{derived_name}'.", icon='INFO')
        elif not resolved_name:
            preview_box.label(text="No texture name is available yet.", icon='ERROR')

        color_box = layout.box()
        color_box.label(text="Color")
        color_box.prop(material, "diffuse_color")
      

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
        context.scene.CurAnimation = len(context.scene.AnimationCollection) - 1
        return {'FINISHED'}

class OPDeleteElement(bpy.types.Operator):
    bl_idname = "bz.deleteanimelement"
    bl_label = "Delete Element"
    bl_description = "Delete the currently selected animation element"

    def execute(self, context):
        scene = context.scene
        if len(scene.AnimationCollection) == 0 or scene.CurAnimation >= len(scene.AnimationCollection):
            self.report({'ERROR'}, "No animation element selected.")
            return {'CANCELLED'}
        scene.AnimationCollection.remove(scene.CurAnimation)
        scene.CurAnimation = min(scene.CurAnimation, len(scene.AnimationCollection) - 1)
        if len(scene.AnimationCollection) == 0:
            scene.CurAnimation = 0
        return {'FINISHED'}


class OPDuplicateElement(bpy.types.Operator):
    bl_idname = "bz.duplicateanimelement"
    bl_label = "Duplicate Element"
    bl_description = "Duplicate the currently selected animation element"

    def execute(self, context):
        scene = context.scene
        if len(scene.AnimationCollection) == 0 or scene.CurAnimation >= len(scene.AnimationCollection):
            self.report({'ERROR'}, "No animation element selected.")
            return {'CANCELLED'}

        source_index = scene.CurAnimation
        source_item = scene.AnimationCollection[source_index]
        new_item = scene.AnimationCollection.add()
        _copy_animation_item(source_item, new_item)
        new_index = len(scene.AnimationCollection) - 1
        target_index = source_index + 1
        scene.AnimationCollection.move(new_index, target_index)
        scene.CurAnimation = target_index
        return {'FINISHED'}


class OPMoveElement(bpy.types.Operator):
    bl_idname = "bz.moveanimelement"
    bl_label = "Move Element"
    bl_description = "Move the selected animation element up or down"

    direction: EnumProperty(
        name="Direction",
        items=(
            ('UP', "Up", "Move the animation element up"),
            ('DOWN', "Down", "Move the animation element down"),
        ),
        default='UP',
    )

    def execute(self, context):
        scene = context.scene
        index = scene.CurAnimation
        count = len(scene.AnimationCollection)
        if count == 0 or index >= count:
            self.report({'ERROR'}, "No animation element selected.")
            return {'CANCELLED'}

        if self.direction == 'UP':
            if index <= 0:
                return {'CANCELLED'}
            scene.AnimationCollection.move(index, index - 1)
            scene.CurAnimation = index - 1
        else:
            if index >= count - 1:
                return {'CANCELLED'}
            scene.AnimationCollection.move(index, index + 1)
            scene.CurAnimation = index + 1
        return {'FINISHED'}


class OPApplyAnimationPreset(bpy.types.Operator):
    bl_idname = "bz.apply_animation_preset"
    bl_label = "Add Animation Preset"
    bl_description = "Append a preset set of animation slots as a starting point"

    preset: EnumProperty(
        name="Preset",
        items=ANIMATION_PRESET_ITEMS,
        default='DEPLOY_PAIR',
    )

    def execute(self, context):
        scene = context.scene
        indices = ANIMATION_PRESET_SLOTS.get(self.preset, [])
        if not indices:
            self.report({'ERROR'}, "Unknown animation preset.")
            return {'CANCELLED'}

        for index_value in indices:
            item = scene.AnimationCollection.add()
            item.Index = index_value
            item.Start = 0
            item.Length = 0
            item.Loop = 1
            item.Speed = 15.0

        scene.CurAnimation = len(scene.AnimationCollection) - 1
        self.report({'INFO'}, f"Added {len(indices)} slots from the preset.")
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


class OPCreateSpinnerHelper(bpy.types.Operator):
    bl_idname = "bz.create_spinner_helper"
    bl_label = "Create Spinner Helper"
    bl_description = "Create a spinner helper object linked to the active GEO for VDF spinner export"

    def execute(self, context):
        src = context.view_layer.objects.active
        if src is None:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}

        if len(src.name) < 5:
            self.report({'ERROR'}, "Active object name must be at least 5 characters")
            return {'CANCELLED'}

        src_name = src.name.lower()
        lod_char = src_name[3] if len(src_name) >= 4 else '1'
        lod = 1 if lod_char not in ['1', '2', '3'] else int(lod_char)
        fixed_src_name = fixgeoname(src.name, lod).lower()

        helper_base = (fixed_src_name[:7] + "t")[:8]
        helper_name = helper_base
        if bpy.data.objects.get(helper_name) is not None:
            for i in range(10):
                candidate = (helper_base[:7] + str(i))[:8]
                if bpy.data.objects.get(candidate) is None:
                    helper_name = candidate
                    break
            else:
                self.report({'ERROR'}, "Unable to find a unique spinner helper name")
                return {'CANCELLED'}

        helper = bpy.data.objects.new(helper_name, None)
        helper.empty_display_type = 'ARROWS'
        helper.empty_display_size = 0.25
        context.collection.objects.link(helper)

        helper.parent = src
        helper.matrix_parent_inverse = src.matrix_world.inverted()
        helper.location = (0.0, 0.0, 0.0)
        helper.rotation_euler = (0.0, 0.0, 0.0)
        helper.scale = (1.0, 1.0, 1.0)

        geo = helper.GEOPropertyGroup
        geo.GEOType = 15
        geo.IsSpinnerHelper = True
        geo.SpinnerTarget = fixed_src_name
        geo.SpinnerAxis = (1.0, 0.0, 0.0)
        geo.SpinnerSpeed = 1.0
        geo.GenerateCollision = False

        helper.hide_render = True

        for obj in context.selected_objects:
            obj.select_set(False)
        helper.select_set(True)
        context.view_layer.objects.active = helper

        self.report({'INFO'}, f"Created spinner helper '{helper.name}' for '{fixed_src_name}'")
        return {'FINISHED'}


class OPCaptureRawVDFMatrix(bpy.types.Operator):
    bl_idname = "bz.capture_raw_vdf_matrix"
    bl_label = "Capture Raw VDF Matrix"
    bl_description = "Capture the active object's current transform into Raw VDF Matrix using export axis conventions"

    def execute(self, context):
        obj = context.view_layer.objects.active
        if obj is None:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}

        geo = getattr(obj, "GEOPropertyGroup", None)
        if geo is None:
            self.report({'ERROR'}, "Active object has no GEO properties")
            return {'CANCELLED'}

        euler = mathutils.Euler((0.0, math.radians(45.0), 0.0), 'YZX')
        euler[:] = obj.rotation_euler.x, obj.rotation_euler.z, obj.rotation_euler.y
        rot_matrix = euler.to_matrix()

        sx, sy, sz = obj.scale
        scale_mat = mathutils.Matrix((
            (sx, 0.0, 0.0),
            (0.0, sy, 0.0),
            (0.0, 0.0, sz),
        ))
        thematrix = rot_matrix @ scale_mat

        translation = obj.matrix_local.to_translation()
        raw = (
            thematrix[0][0], thematrix[0][1], thematrix[0][2],
            thematrix[1][0], thematrix[1][1], thematrix[1][2],
            thematrix[2][0], thematrix[2][1], thematrix[2][2],
            translation.x, translation.z, translation.y,
        )

        geo.RawVDFMatrix = raw
        geo.UseRawVDFMatrix = True

        self.report({'INFO'}, "Captured current transform into Raw VDF Matrix")
        return {'FINISHED'}
        
'''
Animation UIList - Used to make a list of all the animation elements, allowing you to click them to select them.
Animation Panel - Used to hold the UIList, buttons, and all the good stuff including the "animation editor"
'''
class AnimationUIList(bpy.types.UIList):
    bl_idname = "SCENE_UL_Battlezone_ANIM_Element"
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=f"Index {item.Index}")
        row.label(text=f"Start {item.Start}")
        row.label(text=f"Length {item.Length}")
        row.label(text=f"Loop {item.Loop}")
        row.label(text=f"Speed {item.Speed:g}")
        
# And now we can use this list everywhere in Blender. Here is a small example panel.
class AnimationPanel(bpy.types.Panel):
    bl_label = "Battlezone Animations"
    bl_idname = "SCENE_PT_Battlezone_ANIM"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "SCENE_PT_BZ_SDFVDF"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        box = layout.box()
        box.label(text="Animation Elements")
        box.template_list("SCENE_UL_Battlezone_ANIM_Element", "", scene, "AnimationCollection", scene, "CurAnimation")

        actions = layout.box()
        actions.label(text="Actions")
        row = actions.row(align=True)
        row.operator('bz.createanimelement', text="New Element")
        row.operator('bz.duplicateanimelement', text="Duplicate")
        row.operator('bz.deleteanimelement', text="Delete Element")
        move_row = actions.row(align=True)
        move_up = move_row.operator('bz.moveanimelement', text="Move Up")
        move_up.direction = 'UP'
        move_down = move_row.operator('bz.moveanimelement', text="Move Down")
        move_down.direction = 'DOWN'
        actions.operator_menu_enum('bz.apply_animation_preset', "preset", text="Add Preset Slots")

        editor = layout.box()
        editor.label(text="Selected Element")
        if len(scene.AnimationCollection) > 0 and scene.CurAnimation < len(scene.AnimationCollection):
            item = scene.AnimationCollection[scene.CurAnimation]
            editor.prop(item, "Index")
            editor.label(text=_get_animation_index_hint(item.Index), icon='INFO')
            timing = editor.box()
            timing.label(text="Timing")
            timing.prop(item, "Start")
            timing.prop(item, "Length")
            timing.prop(item, "Loop")
            timing.prop(item, "Speed")

            advanced = editor.box()
            advanced.label(text="Advanced")
            advanced.prop(item, "UseCustomUnknownGeoMask")
            if item.UseCustomUnknownGeoMask:
                for i in range(0, 32, 8):
                    row = advanced.row(align=True)
                    row.prop(item, "UnknownGeoMask", index=i+0, text=str(i+0))
                    row.prop(item, "UnknownGeoMask", index=i+1, text=str(i+1))
                    row.prop(item, "UnknownGeoMask", index=i+2, text=str(i+2))
                    row.prop(item, "UnknownGeoMask", index=i+3, text=str(i+3))
                    row.prop(item, "UnknownGeoMask", index=i+4, text=str(i+4))
                    row.prop(item, "UnknownGeoMask", index=i+5, text=str(i+5))
                    row.prop(item, "UnknownGeoMask", index=i+6, text=str(i+6))
                    row.prop(item, "UnknownGeoMask", index=i+7, text=str(i+7))
        else:
            editor.label(text="No animation element selected.", icon='INFO')

        # Animation index reference helper
        ref_box = layout.box()
        ref_box.label(text="Animation Index Reference")
        ref_box.label(text="Index meaning depends on classLabel. Use this as a quick lookup.")
        ref_box.operator(
            "bz.show_anim_index_reference",
            text="Show Animation Index Reference",
            icon='INFO'
        )


class BZ98TOOLS_OT_apply_export_preset(bpy.types.Operator):
    bl_idname = "bz.apply_export_preset"
    bl_label = "Apply Export Preset"
    bl_description = "Apply a built-in or saved export preset to the active export dialog"

    export_kind: StringProperty(name="Export Kind", default="")
    preset_key: StringProperty(name="Preset Key", default="")
    custom_label: StringProperty(name="Custom Label", default="")

    def execute(self, context):
        operator = _get_active_export_operator(context, self.export_kind)
        if operator is None:
            self.report({'ERROR'}, "No matching export dialog is active.")
            return {'CANCELLED'}

        if self.custom_label:
            values = _load_custom_export_preset(self.export_kind, self.custom_label)
            preset_label = self.custom_label
        else:
            values = _get_builtin_export_preset(self.export_kind, self.preset_key)
            preset_label = self.preset_key

        if values is None:
            self.report({'ERROR'}, "Preset could not be loaded.")
            return {'CANCELLED'}

        _apply_export_preset_values(operator, self.export_kind, values)
        self.report({'INFO'}, f"Applied preset '{preset_label}'.")
        return {'FINISHED'}


class BZ98TOOLS_OT_save_export_preset(bpy.types.Operator):
    bl_idname = "bz.save_export_preset"
    bl_label = "Save Export Preset"
    bl_description = "Save the current export settings as a reusable preset"

    export_kind: StringProperty(name="Export Kind", default="")
    preset_name: StringProperty(name="Preset Name", default="")

    def invoke(self, context, event):
        if not self.preset_name:
            self.preset_name = f"{self.export_kind.lower()}_preset"
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "preset_name")

    def execute(self, context):
        operator = _get_active_export_operator(context, self.export_kind)
        if operator is None:
            self.report({'ERROR'}, "No matching export dialog is active.")
            return {'CANCELLED'}

        preset_name = (self.preset_name or "").strip()
        if not preset_name:
            self.report({'ERROR'}, "Preset name cannot be empty.")
            return {'CANCELLED'}

        preset_dir = get_export_preset_dir(self.export_kind)
        os.makedirs(preset_dir, exist_ok=True)
        filename = _normalize_preset_filename(preset_name) + ".json"
        path = os.path.join(preset_dir, filename)
        payload = {
            "label": preset_name,
            "export_kind": self.export_kind,
            "values": _serialize_export_operator(operator, self.export_kind),
        }
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        self.report({'INFO'}, f"Saved preset '{preset_name}'.")
        return {'FINISHED'}


class BZ98TOOLS_OT_delete_export_preset(bpy.types.Operator):
    bl_idname = "bz.delete_export_preset"
    bl_label = "Delete Export Preset"
    bl_description = "Delete a saved export preset"

    export_kind: StringProperty(name="Export Kind", default="")
    custom_label: StringProperty(name="Custom Label", default="")

    def execute(self, context):
        custom_label = (self.custom_label or "").strip()
        if not custom_label:
            self.report({'ERROR'}, "No preset name was provided.")
            return {'CANCELLED'}

        for entry in _list_custom_export_presets(self.export_kind):
            if entry["label"] != custom_label:
                continue
            try:
                os.remove(entry["path"])
            except OSError as exc:
                self.report({'ERROR'}, f"Could not delete preset: {exc}")
                return {'CANCELLED'}
            self.report({'INFO'}, f"Deleted preset '{custom_label}'.")
            return {'FINISHED'}

        self.report({'ERROR'}, f"Could not find preset '{custom_label}'.")
        return {'CANCELLED'}


class BZ98TOOLS_MT_geo_export_presets(bpy.types.Menu):
    bl_idname = "BZ98TOOLS_MT_geo_export_presets"
    bl_label = "GEO Presets"

    def draw(self, context):
        _draw_export_preset_menu_entries(self.layout, "GEO")


class BZ98TOOLS_MT_vdf_export_presets(bpy.types.Menu):
    bl_idname = "BZ98TOOLS_MT_vdf_export_presets"
    bl_label = "VDF Presets"

    def draw(self, context):
        _draw_export_preset_menu_entries(self.layout, "VDF")


class BZ98TOOLS_MT_sdf_export_presets(bpy.types.Menu):
    bl_idname = "BZ98TOOLS_MT_sdf_export_presets"
    bl_label = "SDF Presets"

    def draw(self, context):
        _draw_export_preset_menu_entries(self.layout, "SDF")


class BZ98TOOLS_MT_geo_delete_export_preset(bpy.types.Menu):
    bl_idname = "BZ98TOOLS_MT_geo_delete_export_preset"
    bl_label = "Delete GEO Preset"

    def draw(self, context):
        _draw_export_preset_menu_entries(self.layout, "GEO", delete_mode=True)


class BZ98TOOLS_MT_vdf_delete_export_preset(bpy.types.Menu):
    bl_idname = "BZ98TOOLS_MT_vdf_delete_export_preset"
    bl_label = "Delete VDF Preset"

    def draw(self, context):
        _draw_export_preset_menu_entries(self.layout, "VDF", delete_mode=True)


class BZ98TOOLS_MT_sdf_delete_export_preset(bpy.types.Menu):
    bl_idname = "BZ98TOOLS_MT_sdf_delete_export_preset"
    bl_label = "Delete SDF Preset"

    def draw(self, context):
        _draw_export_preset_menu_entries(self.layout, "SDF", delete_mode=True)


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
        
        return import_geo.load(context, **keywords)
        
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
        return import_vdf.load(context, **keywords)
        
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
        return import_sdf.load(context, **keywords)
        
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

        issues = bz_validation.collect_legacy_validation_issues(context, export_mode="GEO")
        _store_validation_results(context.scene, issues)
        counts = _get_validation_counts(context.scene, export_mode="GEO")
        if counts["ERROR"] > 0:
            self.report(
                {'ERROR'},
                f"GEO export blocked by {counts['ERROR']} validation errors. Run 'Validate Battlezone Scene' for details.",
            )
            return {'CANCELLED'}
        if counts["WARNING"] > 0:
            self.report(
                {'WARNING'},
                f"GEO export validation found {counts['WARNING']} warnings.",
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

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        _draw_export_preset_box(layout, "GEO")

        core = layout.box()
        core.label(text="Core Export")
        active_obj = getattr(getattr(context.view_layer, "objects", None), "active", None)
        if active_obj is None:
            core.label(text="No active object selected.", icon='ERROR')
        else:
            core.label(text=f"Active Object: {active_obj.name}", icon='OBJECT_DATA')
            core.label(text="Only the active mesh object is exported.", icon='INFO')

        _draw_validation_summary_box(layout, scene, export_mode="GEO")

        port = layout.box()
        port.label(text="Create Redux Files")
        port.prop(self, "auto_port_ogre")
        if self.auto_port_ogre:
            _draw_shared_autoport_options(port, self)

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

        issues = bz_validation.collect_legacy_validation_issues(context, export_mode="VDF")
        _store_validation_results(context.scene, issues)
        counts = _get_validation_counts(context.scene, export_mode="VDF")
        if counts["ERROR"] > 0:
            self.report(
                {'ERROR'},
                f"VDF export blocked by {counts['ERROR']} validation errors. Run 'Validate Battlezone Scene' for details.",
            )
            return {'CANCELLED'}
        if counts["WARNING"] > 0:
            self.report(
                {'WARNING'},
                f"VDF export validation found {counts['WARNING']} warnings.",
            )

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

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        _draw_export_preset_box(layout, "VDF")

        core = layout.box()
        core.label(text="Core Export")
        core.label(text="Exports scene GEO slots plus VDF container data.", icon='INFO')

        anim_box = layout.box()
        anim_box.label(text="Animations")
        anim_box.prop(self, "ExportAnimations")
        anim_count = len(getattr(scene, "AnimationCollection", []))
        anim_box.label(text=f"Scene animation elements: {anim_count}")

        legacy = layout.box()
        legacy.label(text="Legacy Output")
        legacy.prop(self, "ExportVDFOnly")
        if not self.ExportVDFOnly:
            legacy.label(text="Referenced GEO files in the export folder may be overwritten.", icon='ERROR')

        _draw_validation_summary_box(layout, scene, export_mode="VDF")

        port = layout.box()
        port.label(text="Create BZR Files")
        port.prop(self, "auto_port_ogre")
        if self.auto_port_ogre:
            _draw_shared_autoport_options(port, self)
            _draw_vdf_autoport_options(port, self)

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

        issues = bz_validation.collect_legacy_validation_issues(context, export_mode="SDF")
        _store_validation_results(context.scene, issues)
        counts = _get_validation_counts(context.scene, export_mode="SDF")
        if counts["ERROR"] > 0:
            self.report(
                {'ERROR'},
                f"SDF export blocked by {counts['ERROR']} validation errors. Run 'Validate Battlezone Scene' for details.",
            )
            return {'CANCELLED'}
        if counts["WARNING"] > 0:
            self.report(
                {'WARNING'},
                f"SDF export validation found {counts['WARNING']} warnings.",
            )

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

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        _draw_export_preset_box(layout, "SDF")

        core = layout.box()
        core.label(text="Core Export")
        core.label(text="Exports scene GEO slots plus SDF container data.", icon='INFO')

        anim_box = layout.box()
        anim_box.label(text="Animations")
        anim_box.prop(self, "ExportAnimations")
        anim_count = len(getattr(scene, "AnimationCollection", []))
        anim_box.label(text=f"Scene animation elements: {anim_count}")

        legacy = layout.box()
        legacy.label(text="Legacy Output")
        legacy.prop(self, "ExportSDFOnly")
        if not self.ExportSDFOnly:
            legacy.label(text="Referenced GEO files in the export folder may be overwritten.", icon='ERROR')

        _draw_validation_summary_box(layout, scene, export_mode="SDF")

        port = layout.box()
        port.label(text="Create BZR Files")
        port.prop(self, "auto_port_ogre")
        if self.auto_port_ogre:
            _draw_shared_autoport_options(port, self)

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
        from .ogrefast import backend as ogre_backend

        xml_converter = self.xml_converter or None

        return ogre_backend.import_mesh(
            self,
            context,
            self.filepath,
            legacy_handler=OgreImport.load,
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
        from .ogrefast import backend as ogre_backend

        xml_converter = self.xml_converter or None

        return ogre_backend.export_mesh(
            self,
            context,
            self.filepath,
            legacy_handler=OgreExport.save,
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

def _get_selected_zfs_entry(scene):
    index = getattr(scene, "zfs_active_index", -1)
    if index < 0 or index >= len(scene.zfs_files):
        return None
    return scene.zfs_files[index]


def _get_zfs_entry_icon(item):
    if item.is_model:
        return 'MESH_DATA'
    if item.ext in ZFS_TEXTURE_EXTENSIONS:
        return 'FILE_IMAGE'
    return 'FILE'


def _get_current_zfs_cache_dir(scene):
    active_zfs_path = getattr(scene, "active_zfs_path", "")
    cache_root = getattr(scene, "zfs_cache_dir", "") or get_default_zfs_cache_dir()
    return get_zfs_archive_cache_dir(active_zfs_path, cache_root)


def _open_path_in_shell(path):
    target_path = os.path.abspath(path)
    if hasattr(bpy.ops, "wm") and hasattr(bpy.ops.wm, "path_open"):
        bpy.ops.wm.path_open(filepath=target_path)
        return
    if hasattr(os, "startfile"):
        os.startfile(target_path)
        return
    raise RuntimeError("No supported path-open handler is available.")


class BZ98TOOLS_MT_import_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_bz98_import"
    bl_label = "Battlezone"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Legacy Formats")
        layout.operator(ImportGEO.bl_idname, text="Geometry (.geo)")
        layout.operator(ImportVDF.bl_idname, text="Vehicle Definition (.vdf)")
        layout.operator(ImportSDF.bl_idname, text="Structure Definition (.sdf)")
        layout.separator()
        layout.label(text="Redux Formats")
        layout.operator(BZ98TOOLS_OT_import_bzr_mesh.bl_idname, text="Redux Mesh (.mesh)")
        layout.separator()
        layout.label(text="Archive Tools")
        layout.operator(BZ98TOOLS_OT_open_zfs.bl_idname, text="Open ZFS Archive (.zfs)")


class BZ98TOOLS_MT_export_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_bz98_export"
    bl_label = "Battlezone"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Legacy Formats")
        layout.operator(ExportGEO.bl_idname, text="Geometry (.geo)")
        layout.operator(ExportVDF.bl_idname, text="Vehicle Definition (.vdf)")
        layout.operator(ExportSDF.bl_idname, text="Structure Definition (.sdf)")
        layout.separator()
        layout.label(text="Redux Formats")
        layout.operator(BZ98TOOLS_OT_export_bzr_mesh.bl_idname, text="Redux Mesh (.mesh)")


def menu_func_import(self, context):
    self.layout.menu(BZ98TOOLS_MT_import_menu.bl_idname, text="Battlezone")
    
def menu_func_export(self, context):
    self.layout.menu(BZ98TOOLS_MT_export_menu.bl_idname, text="Battlezone")


Properties = [
    AnimationPropertyGroup,
    GEOPropertyGroup,
    SDFVDFPropertyGroup,
    MaterialPropertyGroup,
    ValidationIssuePropertyGroup,
]

class ZFSFileEntry(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    ext: bpy.props.StringProperty(name="Extension")
    is_model: bpy.props.BoolProperty(name="Is Model", default=False)

def find_zfs_dependencies(reader, filename, extracted_files, temp_dir):
    """Recursively find and extract dependencies (GEOs and textures) from ZFS."""
    if filename.lower() in extracted_files:
        return

    path = reader.extract(filename, temp_dir)
    if not path:
        print(f"[BZ ZFS] Missing dependency '{filename}' in archive.")
        return
    extracted_files.add(filename.lower())

    ext = os.path.splitext(filename)[1].lower()

    if ext == '.vdf':
        from . import vdf_classes
        try:
            with open(path, 'rb') as f:
                content = f.read()
                pos = 20 # Skip VDFHeader
                vdfc = vdf_classes.VDFCHeader()
                pos = vdfc.Read(content, pos)
                pos += 8 # Skip EXIT
                vgeo = vdf_classes.VGEOHeader()
                pos = vgeo.Read(content, pos)
                for _ in range(vgeo.geocount * 28):
                    geo = vdf_classes.GEOData()
                    geo.Read(content, pos)
                    pos += 100
                    if geo.name.lower() != 'null':
                        find_zfs_dependencies(reader, geo.name + ".geo", extracted_files, temp_dir)
        except Exception as exc:
            print(f"[BZ ZFS] Failed to scan VDF dependencies for '{filename}': {exc}")

    elif ext == '.sdf':
        from . import sdf_classes
        try:
            with open(path, 'rb') as f:
                content = f.read()
                pos = 20 # Skip SDFHeader
                sdfc = sdf_classes.SDFCHeader()
                pos = sdfc.Read(content, pos)
                sgeo = sdf_classes.SGEOHeader()
                pos = sgeo.Read(content, pos)
                for _ in range(sgeo.geocount):
                    geo = sdf_classes.GEOData()
                    geo.Read(content, pos)
                    pos += 120
                    if geo.name.lower() != 'null':
                        find_zfs_dependencies(reader, geo.name + ".geo", extracted_files, temp_dir)
        except Exception as exc:
            print(f"[BZ ZFS] Failed to scan SDF dependencies for '{filename}': {exc}")

    elif ext == '.geo':
        # Scan for textures
        try:
            with open(path, 'rb') as f:
                header_data = struct.unpack('<4si16sIII', f.read(36))
                faces_count = header_data[4]
                f.seek(36 + header_data[3] * 12 + faces_count * 12) # Skip header + verts + normals
                # Actually, parsing GEO is complex, but textures are usually 16-byte strings in GEOFace
                # Let's use a robust scan for common texture extensions
                f.seek(0)
                content = f.read()
                import re
                # Find .map, .pic, .tga references
                tex_matches = re.findall(br'([a-zA-Z0-9_.-]+)\.(map|pic|tga|dds|png|bmp)', content, re.IGNORECASE)
                for tex_name, tex_ext in tex_matches:
                    full_tex = tex_name.decode('ascii', errors='ignore') + "." + tex_ext.decode('ascii', errors='ignore')
                    find_zfs_dependencies(reader, full_tex, extracted_files, temp_dir)
        except Exception as exc:
            print(f"[BZ ZFS] Failed to scan GEO dependencies for '{filename}': {exc}")

class BZ98TOOLS_OT_open_zfs(bpy.types.Operator, ImportHelper):
    """Open a Battlezone ZFS archive to browse its contents"""
    bl_idname = "bz.open_zfs"
    bl_label = "Open ZFS Archive"
    filename_ext = ".zfs"
    filter_glob: bpy.props.StringProperty(default="*.zfs", options={'HIDDEN'})

    def execute(self, context):
        from .zfs_reader import ZFSReader
        context.scene.active_zfs_path = self.filepath
        context.scene.zfs_active_cache_path = get_zfs_archive_cache_dir(
            self.filepath,
            context.scene.zfs_cache_dir.strip() or get_default_zfs_cache_dir(),
        )
        context.scene.zfs_last_import_path = ""
        reader = ZFSReader(self.filepath)
        try:
            reader.open()
            context.scene.zfs_files.clear()
            for name in reader.list_files():
                item = context.scene.zfs_files.add()
                item.name = name
                item.ext = os.path.splitext(name)[1].lower()
                item.is_model = item.ext in {'.vdf', '.sdf', '.geo'}
            first_model_index = next((idx for idx, item in enumerate(context.scene.zfs_files) if item.is_model), -1)
            context.scene.zfs_active_index = first_model_index if first_model_index >= 0 else (0 if len(context.scene.zfs_files) > 0 else -1)
            reader.close()
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open ZFS: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}


class BZ98TOOLS_OT_open_zfs_cache_folder(bpy.types.Operator):
    """Open the configured ZFS cache folder or the active archive cache folder"""
    bl_idname = "bz.open_zfs_cache_folder"
    bl_label = "Open ZFS Cache Folder"

    scope: EnumProperty(
        name="Scope",
        items=(
            ('ROOT', "Root Cache", "Open the root ZFS cache folder"),
            ('ARCHIVE', "Archive Cache", "Open the cache folder for the active ZFS archive"),
        ),
        default='ARCHIVE',
    )

    def execute(self, context):
        scene = context.scene
        if self.scope == 'ROOT':
            target_dir = os.path.abspath(scene.zfs_cache_dir.strip() or get_default_zfs_cache_dir())
        else:
            target_dir = _get_current_zfs_cache_dir(scene)
            if not target_dir:
                self.report({'ERROR'}, "No active ZFS archive is selected.")
                return {'CANCELLED'}

        os.makedirs(target_dir, exist_ok=True)
        try:
            _open_path_in_shell(target_dir)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not open cache folder: {exc}")
            return {'CANCELLED'}
        return {'FINISHED'}


class BZ98TOOLS_OT_clear_zfs_cache(bpy.types.Operator):
    """Delete extracted ZFS cache files"""
    bl_idname = "bz.clear_zfs_cache"
    bl_label = "Clear ZFS Cache"

    def execute(self, context):
        import shutil

        cache_dir = context.scene.zfs_cache_dir.strip() or get_default_zfs_cache_dir()
        cache_dir = os.path.abspath(cache_dir)
        if not os.path.isdir(cache_dir):
            self.report({'INFO'}, "ZFS cache folder is already empty")
            return {'FINISHED'}

        removed = 0
        failures = 0
        for entry in os.listdir(cache_dir):
            path = os.path.join(cache_dir, entry)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                removed += 1
            except OSError:
                failures += 1

        if failures:
            self.report({'WARNING'}, f"Cleared {removed} cache entries, but {failures} could not be removed")
        else:
            self.report({'INFO'}, f"Cleared {removed} cache entries")
        context.scene.zfs_last_import_path = ""
        return {'FINISHED'}


class BZ98TOOLS_OT_clear_zfs_archive_cache(bpy.types.Operator):
    """Delete extracted cache files for the active ZFS archive"""
    bl_idname = "bz.clear_zfs_archive_cache"
    bl_label = "Clear Active Archive Cache"

    def execute(self, context):
        import shutil

        archive_cache_dir = _get_current_zfs_cache_dir(context.scene)
        if not archive_cache_dir:
            self.report({'ERROR'}, "No active ZFS archive is selected.")
            return {'CANCELLED'}

        if not os.path.isdir(archive_cache_dir):
            self.report({'INFO'}, "The active archive cache is already empty.")
            return {'FINISHED'}

        try:
            shutil.rmtree(archive_cache_dir)
        except OSError as exc:
            self.report({'ERROR'}, f"Could not clear archive cache: {exc}")
            return {'CANCELLED'}

        last_import = getattr(context.scene, "zfs_last_import_path", "")
        if last_import and os.path.abspath(last_import).startswith(os.path.abspath(archive_cache_dir)):
            context.scene.zfs_last_import_path = ""

        self.report({'INFO'}, "Cleared the active archive cache.")
        return {'FINISHED'}

class BZ98TOOLS_OT_import_from_zfs(bpy.types.Operator):
    """Extract and import the selected model from ZFS"""
    bl_idname = "bz.import_from_zfs"
    bl_label = "Import from ZFS"
    
    filename: bpy.props.StringProperty()

    def execute(self, context):
        from .zfs_reader import ZFSReader
        zfs_path = context.scene.active_zfs_path
        if not zfs_path or not os.path.exists(zfs_path):
            self.report({'ERROR'}, "No active ZFS archive")
            return {'CANCELLED'}

        filename = self.filename
        if not filename:
            selected = _get_selected_zfs_entry(context.scene)
            if not selected:
                self.report({'ERROR'}, "No ZFS file is selected")
                return {'CANCELLED'}
            filename = selected.name

        cache_root = context.scene.zfs_cache_dir.strip() or get_default_zfs_cache_dir()
        temp_dir = get_zfs_archive_cache_dir(zfs_path, cache_root)
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            reader = ZFSReader(zfs_path)
            reader.open()
            
            extracted_files = set()
            find_zfs_dependencies(reader, filename, extracted_files, temp_dir)
            
            reader.close()

            main_path = os.path.join(temp_dir, filename)
            if not os.path.exists(main_path):
                self.report({'ERROR'}, f"Failed to extract {filename}")
                return {'CANCELLED'}

            ext = os.path.splitext(filename)[1].lower()
            if ext == '.vdf':
                from . import import_vdf
                import_vdf.load(context, main_path)
            elif ext == '.sdf':
                from . import import_sdf
                import_sdf.load(context, main_path)
            elif ext == '.geo':
                from . import import_geo
                import_geo.geoload(context, main_path)
            else:
                self.report({'ERROR'}, f"Unsupported ZFS import type: {ext}")
                return {'CANCELLED'}

            context.scene.zfs_active_cache_path = temp_dir
            context.scene.zfs_last_import_path = main_path
            
            self.report({'INFO'}, f"Successfully imported {filename} and dependencies")
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
        finally:
            # Keep extracted dependencies in the cache folder so imported textures
            # remain available to Blender until the user clears the cache manually.
            pass

        return {'FINISHED'}

class BZ98TOOLS_UL_zfs_files(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name, icon=_get_zfs_entry_icon(item))
        row.label(text=item.ext or "file")

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flags = []

        filter_text = data.zfs_filter.strip().lower()
        type_filter = data.zfs_type_filter

        for item in items:
            matches_text = not filter_text or filter_text in item.name.lower()
            matches_type = (
                type_filter == 'ALL'
                or (type_filter == 'MODELS' and item.is_model)
                or (type_filter == 'TEXTURES' and item.ext in ZFS_TEXTURE_EXTENSIONS)
                or (type_filter == 'OTHER' and not item.is_model and item.ext not in ZFS_TEXTURE_EXTENSIONS)
            )
            flags.append(self.bitflag_filter_item if (matches_text and matches_type) else 0)

        order = bpy.types.UI_UL_list.sort_items_by_name(items, "name")
        return flags, order


class BZ98TOOLS_PT_zfs_explorer(bpy.types.Panel):
    bl_idname = "SCENE_PT_BZ_ZFS"
    bl_label = "Battlezone ZFS Explorer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "SCENE_PT_BZ_SDFVDF"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        archive_cache_dir = _get_current_zfs_cache_dir(scene)
        if archive_cache_dir and scene.zfs_active_cache_path != archive_cache_dir:
            scene.zfs_active_cache_path = archive_cache_dir
        
        layout.operator("bz.open_zfs", icon='FILE_FOLDER')

        cache_box = layout.box()
        cache_box.label(text="Cache")
        cache_box.prop(scene, "zfs_cache_dir", text="Folder")
        cache_actions = cache_box.row(align=True)
        root_open = cache_actions.operator("bz.open_zfs_cache_folder", text="Open Root", icon='FILE_FOLDER')
        root_open.scope = 'ROOT'
        cache_actions.operator("bz.clear_zfs_cache", icon='TRASH')
        
        if scene.active_zfs_path:
            archive_box = layout.box()
            archive_box.label(text=f"Archive: {os.path.basename(scene.active_zfs_path)}", icon='FILE_FOLDER')
            archive_box.label(text=f"Files indexed: {len(scene.zfs_files)}")
            archive_path_row = archive_box.row()
            archive_path_row.enabled = False
            archive_path_row.prop(scene, "active_zfs_path", text="Archive Path")
            cache_dir_row = archive_box.row()
            cache_dir_row.enabled = False
            cache_dir_row.prop(scene, "zfs_active_cache_path", text="Cache Path")
            archive_actions = archive_box.row(align=True)
            archive_open = archive_actions.operator("bz.open_zfs_cache_folder", text="Open Archive Cache", icon='FILE_FOLDER')
            archive_open.scope = 'ARCHIVE'
            archive_actions.operator("bz.clear_zfs_archive_cache", icon='TRASH')
            if scene.zfs_last_import_path:
                last_row = archive_box.row()
                last_row.enabled = False
                last_row.prop(scene, "zfs_last_import_path", text="Last Extracted")

            filters = layout.box()
            filters.label(text="Browser")
            row = filters.row(align=True)
            row.prop(scene, "zfs_filter", text="", icon='VIEWZOOM')
            row.prop(scene, "zfs_type_filter", text="")

            list_box = layout.box()
            list_box.template_list(
                "BZ98TOOLS_UL_zfs_files",
                "",
                scene,
                "zfs_files",
                scene,
                "zfs_active_index",
                rows=10,
            )

            selected = _get_selected_zfs_entry(scene)
            action_box = layout.box()
            action_box.label(text="Selection")
            if selected:
                action_box.label(text=selected.name, icon=_get_zfs_entry_icon(selected))
                import_row = action_box.row()
                import_row.enabled = selected.is_model
                op = import_row.operator("bz.import_from_zfs", text="Import Selected", icon='IMPORT')
                op.filename = selected.name
                if not selected.is_model:
                    action_box.label(text="Only GEO, VDF, and SDF files can be imported directly.", icon='INFO')
            else:
                action_box.label(text="Select a file from the archive list.", icon='INFO')

GUIClasses = [
    BZ98TOOLS_MT_import_menu,
    BZ98TOOLS_MT_export_menu,
    BZ_OT_ShowAnimIndexReference,
    BZ_PT_GeoTypeListPopover,
    BattlezoneSDFVDFProperties,
    BZ98TOOLS_PT_scene_asset_properties,
    BZ98TOOLS_PT_scene_collision_helpers,
    BZ98TOOLS_PT_scene_advanced,
    BZ98TOOLS_OT_validate_scene,
    BZ98TOOLS_OT_select_validation_target,
    BZ98TOOLS_OT_fix_validation_name,
    BZ98TOOLS_PT_validation,
    BattlezoneGEOProperties,
    BZ98TOOLS_PT_geo_collision,
    BZ98TOOLS_PT_geo_sdf,
    BZ98TOOLS_PT_geo_vdf,
    BZ98TOOLS_PT_geo_advanced,
    BZ98TOOLS_OT_fill_material_texture_name,
    BZ98TOOLS_OT_fill_material_texture_from_image,
    BattlezoneMaterialProperties,
    OPCreateNewElement,
    OPDeleteElement,
    OPDuplicateElement,
    OPMoveElement,
    OPApplyAnimationPreset,
    BZ98TOOLS_OT_apply_export_preset,
    BZ98TOOLS_OT_save_export_preset,
    BZ98TOOLS_OT_delete_export_preset,
    BZ98TOOLS_MT_geo_export_presets,
    BZ98TOOLS_MT_vdf_export_presets,
    BZ98TOOLS_MT_sdf_export_presets,
    BZ98TOOLS_MT_geo_delete_export_preset,
    BZ98TOOLS_MT_vdf_delete_export_preset,
    BZ98TOOLS_MT_sdf_delete_export_preset,
    OPGenerateVDFCollisionMeshes,
    OPGenerateCollision,
    OPCreateSpinnerHelper,
    OPCaptureRawVDFMatrix,
    AnimationUIList,
    AnimationPanel,
    BZ98TOOLS_UL_zfs_files,
    BZ98TOOLS_PT_zfs_explorer,
    BZ98TOOLS_OT_open_zfs,
    BZ98TOOLS_OT_open_zfs_cache_folder,
    BZ98TOOLS_OT_clear_zfs_cache,
    BZ98TOOLS_OT_clear_zfs_archive_cache,
    BZ98TOOLS_OT_import_from_zfs,
    ZFSFileEntry,
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

    # ZFS Explorer Properties
    bpy.types.Scene.zfs_files = bpy.props.CollectionProperty(type=ZFSFileEntry)
    bpy.types.Scene.active_zfs_path = bpy.props.StringProperty(name="Active ZFS")
    bpy.types.Scene.zfs_active_cache_path = bpy.props.StringProperty(name="Active ZFS Cache Path")
    bpy.types.Scene.zfs_active_index = bpy.props.IntProperty(name="Active ZFS Entry", default=-1)
    bpy.types.Scene.zfs_filter = bpy.props.StringProperty(name="ZFS Filter")
    bpy.types.Scene.zfs_type_filter = bpy.props.EnumProperty(
        name="ZFS Type Filter",
        items=(
            ('ALL', "All Files", "Show all files"),
            ('MODELS', "Models", "Show importable GEO, VDF, and SDF files"),
            ('TEXTURES', "Textures", "Show texture and image files"),
            ('OTHER', "Other", "Show non-model support files"),
        ),
        default='MODELS',
    )
    bpy.types.Scene.zfs_cache_dir = bpy.props.StringProperty(
        name="ZFS Cache Folder",
        description="Folder used to keep extracted ZFS dependencies available after import",
        default=get_default_zfs_cache_dir(),
        subtype='DIR_PATH',
    )
    bpy.types.Scene.zfs_last_import_path = bpy.props.StringProperty(name="Last ZFS Import Path")
    bpy.types.Scene.bz_validation_issues = bpy.props.CollectionProperty(type=ValidationIssuePropertyGroup)
    bpy.types.Scene.bz_validation_signature = bpy.props.StringProperty(name="Validation Signature")

def unregister():
    # Remove menus first so UI won't try to use unregistered classes
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    # Remove dynamically registered Blender properties.
    for owner, prop_name in (
        (bpy.types.Scene, "AnimationCollection"),
        (bpy.types.Scene, "CurAnimation"),
        (bpy.types.Material, "MaterialPropertyGroup"),
        (bpy.types.Object, "GEOPropertyGroup"),
        (bpy.types.Scene, "SDFVDFPropertyGroup"),
        (bpy.types.Scene, "zfs_files"),
        (bpy.types.Scene, "active_zfs_path"),
        (bpy.types.Scene, "zfs_active_cache_path"),
        (bpy.types.Scene, "zfs_active_index"),
        (bpy.types.Scene, "zfs_filter"),
        (bpy.types.Scene, "zfs_type_filter"),
        (bpy.types.Scene, "zfs_cache_dir"),
        (bpy.types.Scene, "zfs_last_import_path"),
        (bpy.types.Scene, "bz_validation_issues"),
        (bpy.types.Scene, "bz_validation_signature"),
    ):
        if hasattr(owner, prop_name):
            delattr(owner, prop_name)

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
