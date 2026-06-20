import os

ZFS_TEXTURE_EXTENSIONS = {
    ".map",
    ".pic",
    ".tga",
    ".dds",
    ".png",
    ".bmp",
    ".jpg",
    ".jpeg",
}

LEGACY_VEHICLE_FORWARD_LABEL = "Legacy VDF/SDF/GEO vehicle front: Blender +Y"
REDUX_MESH_FORWARD_LABEL = "Direct Redux .mesh vehicle front: Blender -Y"
AUTO_PORT_FORWARD_NOTE = (
    "Legacy + Redux export uses the legacy +Y setup, then converts for Redux."
)

GEO_FACE_PLANE_MODE_ITEMS = (
    (
        "CURRENT",
        "Current Toolkit Default",
        "Write the historical toolkit values: face center X/Y/Z and D = 1.0",
    ),
    (
        "PRESERVE",
        "Preserve Imported",
        "Write imported bz_face_plane_x/y/z/d attributes when present; otherwise use the current default",
    ),
    (
        "RECOMPUTE",
        "Recompute From Faces",
        "Write a normalized face plane and distance from the exported GEO-coordinate vertices",
    ),
    (
        "DX_FIX",
        "DX Normal Distance Fix",
        "Best-effort recreation of the old Max GEO exporter workaround for disappearing triangles; currently recomputes face plane normal and distance",
    ),
)

TERNARY_ITEMS = [
    ("AUTO", "Auto", "Use automatic detection"),
    ("YES", "Force Yes", "Force enabled"),
    ("NO", "Force No", "Force disabled"),
]

ANIMATION_PRESET_ITEMS = (
    (
        "DEPLOY_PAIR",
        "Deploy Pair",
        "Add slots 0 and 1 for common deploy/undeploy workflows",
    ),
    (
        "TURRET_PAIR",
        "Turret Pair",
        "Add slots 0 and 1 for common turret motion workflows",
    ),
    (
        "WALKER_CORE",
        "Walker Core",
        "Add slots 2 through 7 for a typical walker idle and movement set",
    ),
    (
        "PERSON_CORE",
        "Person Core",
        "Add slots 0 through 11 for a broad person animation starter set",
    ),
)

VALIDATION_PRESET_ITEMS = (
    ("AUTO", "General", "Run the standard legacy export checks"),
    (
        "VEHICLE",
        "Vehicle / VDF",
        "Run vehicle-oriented checks, including POV and COL helpers",
    ),
    (
        "TURRET",
        "Turret",
        "Require turret animation slots and turret/cockpit conventions",
    ),
    ("WALKER", "Walker", "Require standard walker animation slots"),
    ("PERSON", "Person", "Require standard person animation slots"),
    ("ANIMATED", "Animated", "Require at least one legacy ANIM sequence entry"),
)

ANIMATION_PRESET_SLOTS = {
    "DEPLOY_PAIR": [0, 1],
    "TURRET_PAIR": [0, 1],
    "WALKER_CORE": [2, 3, 4, 5, 6, 7],
    "PERSON_CORE": list(range(0, 12)),
}

LEGACY_TRANSFORM_DATA_PATHS = {
    "location",
    "rotation_euler",
    "rotation_quaternion",
    "rotation_axis_angle",
    "scale",
}

QUICK_VEHICLE_GEO_SPECS = (
    ("bod", 60, "Body", (0.0, 0.0, 0.0), 0.28),
    ("pov", 40, "POV", (0.0, 0.85, 0.45), 0.12),
    ("gc1", 71, "GC1", (-0.22, 0.7, 0.18), 0.10),
    ("gr1", 72, "GR1", (0.22, 0.7, 0.18), 0.10),
    ("gs1", 74, "GS1", (-0.22, 0.15, 0.18), 0.10),
    ("gm1", 73, "GM1", (0.22, 0.15, 0.18), 0.10),
    ("rot", 66, "Rotor", (-0.45, 0.0, 0.12), 0.12),
    ("nac", 67, "Nacelle", (0.45, 0.0, 0.12), 0.12),
)

EXPORT_KIND_IDNAMES = {
    "GEO": "export_scene.geo",
    "VDF": "export_scene.vdf",
    "SDF": "export_scene.sdf",
}

EXPORT_PRESET_PROPERTY_NAMES = {
    "GEO": (
        "face_plane_mode",
        "auto_port_ogre",
        "ogre_name",
        "ogre_suffix",
        "ogre_flat_colors",
        "ogre_bounds_mult",
        "ogre_act_path",
        "ogre_config_path",
        "ogre_only_once",
        "ogre_nowrite",
        "ogre_skip_unchanged",
        "ogre_profile_export",
        "ogre_dest_dir",
    ),
    "VDF": (
        "ExportAnimations",
        "ExportVDFOnly",
        "face_plane_mode",
        "auto_port_ogre",
        "ogre_name",
        "ogre_suffix",
        "ogre_flat_colors",
        "ogre_bounds_mult",
        "ogre_act_path",
        "ogre_config_path",
        "ogre_only_once",
        "ogre_nowrite",
        "ogre_skip_unchanged",
        "ogre_profile_export",
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
        "ogre_stabilize_walker_cockpit",
    ),
    "SDF": (
        "ExportAnimations",
        "ExportSDFOnly",
        "face_plane_mode",
        "auto_port_ogre",
        "ogre_name",
        "ogre_suffix",
        "ogre_flat_colors",
        "ogre_bounds_mult",
        "ogre_act_path",
        "ogre_config_path",
        "ogre_only_once",
        "ogre_nowrite",
        "ogre_skip_unchanged",
        "ogre_profile_export",
        "ogre_dest_dir",
    ),
}

BUILTIN_EXPORT_PRESETS = {
    "GEO": (
        (
            "classic_geo",
            "Legacy GEO Only",
            {
                "face_plane_mode": "CURRENT",
                "auto_port_ogre": False,
                "ogre_name": "",
                "ogre_suffix": "_port",
                "ogre_flat_colors": False,
                "ogre_bounds_mult": [1.0, 1.0, 1.0],
                "ogre_act_path": "",
                "ogre_config_path": "",
                "ogre_only_once": False,
                "ogre_nowrite": False,
                "ogre_skip_unchanged": True,
                "ogre_profile_export": False,
                "ogre_dest_dir": "",
            },
        ),
        (
            "geo_port",
            "Legacy GEO + Redux",
            {
                "face_plane_mode": "CURRENT",
                "auto_port_ogre": True,
                "ogre_name": "",
                "ogre_suffix": "_port",
                "ogre_flat_colors": False,
                "ogre_bounds_mult": [1.0, 1.0, 1.0],
                "ogre_act_path": "",
                "ogre_config_path": "",
                "ogre_only_once": False,
                "ogre_nowrite": False,
                "ogre_skip_unchanged": True,
                "ogre_profile_export": False,
                "ogre_dest_dir": "",
            },
        ),
    ),
    "VDF": (
        (
            "vehicle_vdf",
            "Legacy Vehicle Only",
            {
                "ExportAnimations": True,
                "ExportVDFOnly": False,
                "face_plane_mode": "CURRENT",
                "auto_port_ogre": False,
                "ogre_name": "",
                "ogre_suffix": "_port",
                "ogre_flat_colors": False,
                "ogre_bounds_mult": [1.0, 1.0, 1.0],
                "ogre_act_path": "",
                "ogre_config_path": "",
                "ogre_only_once": False,
                "ogre_nowrite": False,
                "ogre_skip_unchanged": True,
                "ogre_profile_export": False,
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
                "ogre_scope_transform": [
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                ],
                "ogre_scope_texture": "__scope",
                "ogre_no_pov_rots": False,
                "ogre_stabilize_walker_cockpit": False,
            },
        ),
        (
            "vehicle_vdf_port",
            "Legacy Vehicle + Redux",
            {
                "ExportAnimations": True,
                "ExportVDFOnly": False,
                "face_plane_mode": "CURRENT",
                "auto_port_ogre": True,
                "ogre_name": "",
                "ogre_suffix": "_port",
                "ogre_flat_colors": False,
                "ogre_bounds_mult": [1.0, 1.0, 1.0],
                "ogre_act_path": "",
                "ogre_config_path": "",
                "ogre_only_once": False,
                "ogre_nowrite": False,
                "ogre_skip_unchanged": True,
                "ogre_profile_export": False,
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
                "ogre_scope_transform": [
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                ],
                "ogre_scope_texture": "__scope",
                "ogre_no_pov_rots": False,
                "ogre_stabilize_walker_cockpit": False,
            },
        ),
    ),
    "SDF": (
        (
            "structure_sdf",
            "Legacy Structure Only",
            {
                "ExportAnimations": True,
                "ExportSDFOnly": False,
                "face_plane_mode": "CURRENT",
                "auto_port_ogre": False,
                "ogre_name": "",
                "ogre_suffix": "_port",
                "ogre_flat_colors": False,
                "ogre_bounds_mult": [1.0, 1.0, 1.0],
                "ogre_act_path": "",
                "ogre_config_path": "",
                "ogre_only_once": False,
                "ogre_nowrite": False,
                "ogre_skip_unchanged": True,
                "ogre_profile_export": False,
                "ogre_dest_dir": "",
            },
        ),
        (
            "structure_sdf_port",
            "Legacy Structure + Redux",
            {
                "ExportAnimations": True,
                "ExportSDFOnly": False,
                "face_plane_mode": "CURRENT",
                "auto_port_ogre": True,
                "ogre_name": "",
                "ogre_suffix": "_port",
                "ogre_flat_colors": False,
                "ogre_bounds_mult": [1.0, 1.0, 1.0],
                "ogre_act_path": "",
                "ogre_config_path": "",
                "ogre_only_once": False,
                "ogre_nowrite": False,
                "ogre_skip_unchanged": True,
                "ogre_profile_export": False,
                "ogre_dest_dir": "",
            },
        ),
    ),
}

DUAL_COMPONENT_INFO_LINES = (
    "Battlezone 98 Redux separates legacy gameplay data from rendered visuals.",
    "",
    "Physics / legacy component:",
    "VDF files define vehicle physics, collision, hardpoints, and legacy animation behavior.",
    "SDF files define structure physics, collision, effect points, and legacy animation behavior.",
    "GEO files are the individual movable or animated legacy parts inside VDF/SDF files.",
    "",
    "Visual / animation component:",
    "OGRE .mesh files define rendered vertices, faces, normals, UVs, skin weights, tangents, and colors.",
    "OGRE .skeleton files define the visual bone hierarchy and animations.",
    "Redux skeleton bones should use the same names, orientation, and pivots as matching GEO parts.",
    "Material files define texture and shader assignments for the visual mesh.",
)

ADVANCED_VDF_INFO_LINES = (
    "Advanced VDF editing support:",
    "",
    "Spinner helpers: create a dummy/helper GEO after the target, set it as a Spinner Helper, assign Spinner Target, Axis, and Speed. Export writes Type 15 behavior without manual hex editing.",
    "Axis vector direction controls spin axis; vector magnitude times speed is angular speed in radians per second.",
    "",
    "Raw transform scaling: enable Use Raw VDF Matrix in Experimental, then edit the 12 floats in right, up, front, position order.",
    "This exposes the same transform data normally edited in HxD for hardpoint or visual scaling experiments.",
    "",
    "Keep backups when experimenting with raw VDF transforms. Some scaled hardpoints or helpers can change gameplay behavior.",
)

PIVOT_DUMMYROOT_INFO_LINES = (
    "Pivot and dummyroot notes:",
    "",
    "In Blender, the object origin is the Battlezone GEO pivot. Rotation, explosion behavior, cockpit alignment, POV direction, and emitters all depend on that origin and its local axes.",
    "For rotators, gun barrels, wings, doors, and emitters, place the origin exactly on the intended hinge/emitter point and keep the object's local orientation deliberate.",
    "LOD2 cockpit GEOs should have a matching LOD1 counterpart, be linked/parented to it, and share the same origin and orientation.",
    "",
    "Legacy dummyroot was a makeobj authoring convention. The addon does not require a Blender object named dummyroot.",
    "Use one clean root model hierarchy per export scene. An unparented exportable root GEO writes as WORLD/root in the legacy hierarchy.",
    "Author hover/sink offsets by placing the root/object origins at the intended model reference point, then moving the mesh geometry relative to that origin as needed.",
    "Keep unrelated linked or exportable model hierarchies out of the scene before VDF/SDF export.",
)

VALIDATION_CHECK_LINES = (
    "Validation coverage:",
    "Active GEO export object is selected, is a mesh, and has vertices.",
    "Legacy VDF/SDF names have valid length and LOD markers.",
    "GEO first-character naming best practice is reported as info.",
    "Normalized export names do not collide.",
    "Parents resolve to exportable objects in the same LOD set.",
    "Multiple top-level export roots are warned because unrelated linked models can corrupt legacy output.",
    "LOD2 cockpit counterparts are checked for matching LOD1 part, parent, pivot, and orientation.",
    "LOD3 parts are checked for matching LOD1, low-detail intent, and unneeded Redux usage.",
    "Mesh face topology and material texture names are legacy-safe.",
    "GEO type and common hardpoint suffix combinations are checked.",
    "Armatures, skinning, shape keys, constraints, and unsupported animation channels are flagged.",
    "VDF vehicle essentials are checked: POV/eyepoint and inner_col/outer_col helpers, with structure/producer-style exceptions.",
    "Collision helper names and mesh presence are checked.",
    "Animation presets check required slots for turret, walker, person, and animated workflows.",
    "Animation guide checks report loop first/last pose mismatches, high animated-GEO counts, and preferred legacy frame ranges.",
    "Turret and cockpit conventions are checked, including cockpit rotator matching.",
)

GEO_TYPE_UI_HINTS = {
    1: (
        "ERROR",
        "Type 1 is known to crash as a VDF/SDF GEO. Avoid using it in legacy vehicle/structure exports.",
    ),
    3: (
        "ERROR",
        "Type 3 is known to crash as a VDF/SDF GEO. Avoid using it in legacy vehicle/structure exports.",
    ),
    15: (
        "INFO",
        "Type 15 is used for spinner behavior. Spinner helpers normally export with this role.",
    ),
    38: ("INFO", "Type 38 is typically used as a Redux headlight mask helper."),
    40: (
        "INFO",
        "Type 40 is the POV / eyepoint. For Redux turret cockpits, parent POV under ty# yaw instead of tx# pitch.",
    ),
    65: (
        "INFO",
        "Type 65 is a turret rotator. Use ty# for yaw, tx# for pitch, and keep cockpit geometry off the POV bone.",
    ),
    70: ("INFO", "Type 70 marks a weapon hardpoint or production smoke emitter."),
    71: ("INFO", "Type 71 marks a cannon hardpoint. Use suffix gc1-gc5."),
    72: ("INFO", "Type 72 marks a rocket hardpoint. Use suffix gr1-gr5."),
    73: ("INFO", "Type 73 marks a mortar hardpoint. Use suffix gm1-gm5."),
    74: ("INFO", "Type 74 marks a special hardpoint. Use suffix gs1-gs5."),
    75: (
        "WARNING",
        "Type 75 acts as a flame emitter and usually makes the GEO geometry itself invisible.",
    ),
    76: ("INFO", "Type 76 marks a smoke emitter."),
    77: ("INFO", "Type 77 marks a dust emitter."),
}

geotypes = []
geotype_lookup = {}


def insertgeotypedata(idx, label):
    item = (idx, f"{idx} - {label}", "")
    geotypes.append(item)
    geotype_lookup[idx] = item


# -------------------------------------------------------------------
# GEO CLASS IDs (from Battlezone’s CLASS_ID_* definitions)
# -------------------------------------------------------------------
insertgeotypedata(0, "NONE (Does nothing, part of main object)")
insertgeotypedata(1, "HELICOPTER (Crashes game as VDF/SDF – do not use)")
insertgeotypedata(2, "STRUCTURE1 (Wooden structures, unknown)")
insertgeotypedata(3, "POWERUP (Crashes game as VDF/SDF)")
insertgeotypedata(4, "PERSON (Unknown / untested)")
insertgeotypedata(5, "SIGN (Unknown / untested)")
insertgeotypedata(6, "VEHICLE (Unknown / untested)")
insertgeotypedata(7, "SCRAP (Scrap material)")
insertgeotypedata(
    8, "BRIDGE (Structure containing floor; likely no extra behavior)"
)
insertgeotypedata(9, "FLOOR (Bridge floor; likely no extra behavior)")
insertgeotypedata(10, "STRUCTURE2 (Metal structures)")
insertgeotypedata(11, "SCROUNGE (Faces GEO toward camera)")

# Old “LGT” guess – still unknown, keep for completeness
insertgeotypedata(33, "LGT (Vehicle light? – legacy guess)")

insertgeotypedata(
    15, "SPINNER (Spinner / rotating geo; usable on VDFs & buildings)"
)

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
insertgeotypedata(
    67, "NACELLE_GEOMETRY (Thrust/steering nacelle; W/A/S/D + flame)"
)
insertgeotypedata(68, "FIN_GEOMETRY (Steering fin)")
insertgeotypedata(69, "COCKPIT_GEOMETRY (Cockpit geometry)")

# Hardpoints & emitters
insertgeotypedata(
    70,
    "WEAPON_HARDPOINT (* hardpoint, no default powerups) Also Prod Unit Smoke Emitter",
)
insertgeotypedata(71, "CANNON_HARDPOINT")
insertgeotypedata(72, "ROCKET_HARDPOINT")
insertgeotypedata(73, "MORTAR_HARDPOINT")
insertgeotypedata(74, "SPECIAL_HARDPOINT (where prod unit throws out a build")
insertgeotypedata(
    75,
    "FLAME_EMITTER (Visible on full forward thrust). Makes the geo geometry invisible.",
)
insertgeotypedata(76, "SMOKE_EMITTER")
insertgeotypedata(77, "DUST_EMITTER")

insertgeotypedata(81, "PARKING_LOT (Hangar / supply pad center of effect)")

GEO_TYPE_ENUM_ITEMS = [
    (f"GEO_{idx}", label, label, idx) for idx, label, _ in geotypes
]
