# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

from .spacial import (
	Vector3, Transform
)

VDF_REVISION = 7
SDF_REVISION = 8

class ClassID:
	NONE               = 0x00
	HELICOPTER         = 0x01
	STRUCTURE1         = 0x02
	POWERUP            = 0x03
	PERSON             = 0x04
	SIGN               = 0x05
	VEHICLE            = 0x06
	SCRAP              = 0x07
	BRIDGE             = 0x08
	FLOOR              = 0x09
	STRUCTURE2         = 0x0A
	SCROUNGE           = 0x0B
                               # TERRAIN             = 0x0C
                               # GATE                = 0x0D
                               # ARTILLERY           = 0x0E
	SPINNER            = 0x0F
                               # BAD_16              = 0x10
                               # BAD_17              = 0x11
                               # BAD_18              = 0x12
                               # BAD_19              = 0x13
                               # DRIVER              = 0x14
                               # ENGINE              = 0x15
                               # BRAKE               = 0x16
                               # SUSPENSION          = 0x17
                               # SPECIAL             = 0x18
                               # BAD_25              = 0x19
                               # BAD_26              = 0x1A
                               # RIGHT_MIRROR        = 0x1B
                               # LEFT_MIRROR         = 0x1C
                               # INT_MIRROR          = 0x1D
                               # WHEEL               = 0x1E
                               # STEERING_WHEEL      = 0x1F
                               # RIGHT_HANDGUN       = 0x20
                               # LEFT_HANDGUN        = 0x21
                               # RADAR               = 0x22     # Used by the Czar tank for some reason
                               # SPEEDOMETER         = 0x23
                               # TACHOMETER          = 0x24
                               # NOTEPAD             = 0x25
	HEADLIGHT_MASK     = 0x26
                               # NETWORK_FLAG        = 0x27
	EYEPOINT           = 0x28
                               # POF                 = 0x29
	COM                = 0x2A
                               # BAD_43              = 0x2B
                               # BAD_44              = 0x2C
                               # BAD_45              = 0x2D
                               # BAD_46              = 0x2E
                               # BAD_47              = 0x2F
                               # BAD_48              = 0x30
                               # BAD_49              = 0x31
	WEAPON             = 0x32
	ORDNANCE           = 0x33
	EXPLOSION          = 0x34
	CHUNK              = 0x35
	SORT_OBJECT        = 0x36
	NONCOLLIDABLE      = 0x37
                               # BAD_56              = 0x38
                               # BAD_57              = 0x39
                               # BAD_58              = 0x3A
                               # BAD_59              = 0x3B
	VEHICLE_GEOMETRY   = 0x3C
	STRUCTURE_GEOMETRY = 0x3D
                               # WHEEL_GEOMETRY      = 0x3E
	WEAPON_GEOMETRY    = 0x3F
	ORDNANCE_GEOMETRY  = 0x40
	TURRET_GEOMETRY    = 0x41
	ROTOR_GEOMETRY     = 0x42
	NACELLE_GEOMETRY   = 0x43
	FIN_GEOMETRY       = 0x44
	COCKPIT_GEOMETRY   = 0x45  # BAD_69
	WEAPON_HARDPOINT   = 0x46
	CANNON_HARDPOINT   = 0x47
	ROCKET_HARDPOINT   = 0x48
	MORTAR_HARDPOINT   = 0x49
	SPECIAL_HARDPOINT  = 0x4A
	FLAME_EMITTER      = 0x4B  # EXPLOSION_GEOMETRY
	SMOKE_EMITTER      = 0x4C  # BAD_76
	DUST_EMITTER       = 0x4D  # BAD_77
	                           # BAD_78              = 0x4E
	                           # BAD_79              = 0x4F
	                           # INTERSECTION1       = 0x50
	PARKING_LOT        = 0x51
	                           # INTERSECTION2       = 0x52
	                           # INTERSECTION3       = 0x53
	
	name_map = {
		NONE              : "NONE",
		HELICOPTER        : "HELICOPTER",
		STRUCTURE1        : "STRUCTURE1",
		POWERUP           : "POWERUP",
		PERSON            : "PERSON",
		SIGN              : "SIGN",
		VEHICLE           : "VEHICLE",
		SCRAP             : "SCRAP",
		BRIDGE            : "BRIDGE",
		FLOOR             : "FLOOR",
		STRUCTURE2        : "STRUCTURE2",
		SCROUNGE          : "SCROUNGE",
		SPINNER           : "SPINNER",
		HEADLIGHT_MASK    : "HEADLIGHT_MASK",
		EYEPOINT          : "EYEPOINT",
		COM               : "COM",
		WEAPON            : "WEAPON",
		ORDNANCE          : "ORDNANCE",
		EXPLOSION         : "EXPLOSION",
		CHUNK             : "CHUNK",
		SORT_OBJECT       : "SORT_OBJECT",
		NONCOLLIDABLE     : "NONCOLLIDABLE",
		VEHICLE_GEOMETRY  : "VEHICLE_GEOMETRY",
		STRUCTURE_GEOMETRY: "STRUCTURE_GEOMETRY",
		WEAPON_GEOMETRY   : "WEAPON_GEOMETRY",
		ORDNANCE_GEOMETRY : "ORDNANCE_GEOMETRY",
		TURRET_GEOMETRY   : "TURRET_GEOMETRY",
		ROTOR_GEOMETRY    : "ROTOR_GEOMETRY",
		NACELLE_GEOMETRY  : "NACELLE_GEOMETRY",
		FIN_GEOMETRY      : "FIN_GEOMETRY",
		COCKPIT_GEOMETRY  : "COCKPIT_GEOMETRY",
		WEAPON_HARDPOINT  : "WEAPON_HARDPOINT",
		CANNON_HARDPOINT  : "CANNON_HARDPOINT",
		ROCKET_HARDPOINT  : "ROCKET_HARDPOINT",
		MORTAR_HARDPOINT  : "MORTAR_HARDPOINT",
		SPECIAL_HARDPOINT : "SPECIAL_HARDPOINT",
		FLAME_EMITTER     : "FLAME_EMITTER",
		SMOKE_EMITTER     : "SMOKE_EMITTER",
		DUST_EMITTER      : "DUST_EMITTER",
		PARKING_LOT       : "PARKING_LOT",
	}
	
	
	def label(cid, full=False):
		if(cid in ClassID.name_map):
			if(full):
				return f"{ClassID.name_map[cid]}[0x{cid:02X}]"
			else:
				return ClassID.name_map[cid]
		else:
			return f"ClassID[0x{cid:02X}]"
	
	hardpoint_set = [
		WEAPON_HARDPOINT,
		CANNON_HARDPOINT,
		ROCKET_HARDPOINT,
		MORTAR_HARDPOINT,
		SPECIAL_HARDPOINT,
	]
	
	emitter_set = [
		FLAME_EMITTER,
		SMOKE_EMITTER,
		DUST_EMITTER,
	]
	
	invisible_set = {
		HEADLIGHT_MASK,
		EYEPOINT,
		WEAPON_HARDPOINT,
		CANNON_HARDPOINT,
		ROCKET_HARDPOINT,
		MORTAR_HARDPOINT,
		SPECIAL_HARDPOINT,
		FLAME_EMITTER,
		SMOKE_EMITTER,
		DUST_EMITTER,
	}
	
	@staticmethod
	def is_invisible(cid):
		return cid in invisible_set
	
	@staticmethod
	def is_visible(cid):
		return cid not in invisible_set

class VGEO:
	class LOD:
		PRIMARY = 0
		COCKPIT = 1
		LOWPOLY = 2
		#UNUSED_3
		#UNUSED_4
		#UNUSED_5
		#UNUSED_6
		COUNT = 7
	
	class REP:
		PRIMARY = 0
		#UNUSED_1
		#UNUSED_2
		#UNUSED_3
		COUNT = 4

class SGEO:
	class LOD:
		PRIMARY = 0
		#UNUSED_1
		#UNUSED_2
		COUNT = 3
	
	class REP:
		PRIMARY = 0
		#UNUSED_1
		COUNT = 2

class CollisionPlanes:
	def __init__(self):
		self.front = 0.0
		self.front_middle = 0.0
		self.back_middle = 0.0
		self.back = 0.0
		self.right = 0.0
		self.right_middle = 0.0
		self.left_middle = 0.0
		self.left = 0.0
		self.top = 0.0
		self.top_middle = 0.0
		self.bottom_middle = 0.0
		self.bottom = 0.0

class GeoObject:
	def __init__(self, bwd2, lod, rep, index):
		self.bwd2 = bwd2
		self.lod = lod
		self.rep = rep
		self.index = index
		
		self.name = "NULL"
		self.transform = Transform()
		self.parentname = "NULL"
		self.center_pos = Vector3()
		self.radius = 0
		self.half_size = Vector3()
		self.class_id = ClassID.VEHICLE_GEOMETRY
		self.object_flags = 0
		
		self.ddr = 0
		self.target = Vector3()
		self.time = 0.0
	
	def set_parentname(self, parentname):
		self.parentname = parentname
		low = parentname.lower()
		if(low == 'world' or low == 'null'):
			self.parent = None
		self.parent = self.bwd2.get_object_by_name(parentname)
	
	def set_parent(self, obj):
		self.parentname = obj.name
		self.parent = obj
	
	def is_null(self):
		return self.name.lower() == 'null'
	
	def is_root(self):
		lowparent = self.parentname.lower()
		if(lowparent == 'world'):
			return True
		if(lowparent == 'null'):
			return True
		if(not self.bwd2.object_exists(self.parentname)):
			return True
		return False
	
	
	def get_primary(self, raw=False):
		return self.bwd2.get_primary_object(self.index, raw)
	
	def get_variant(self, lod, rep, raw=False):
		return self.bwd2.get_object(lod, rep, self.index, raw)
	
	def is_primary(self):
		return self.lod == 0 and self.rep == 0
		

class VGeoObject(GeoObject):
	def __init__(self, bwd2, lod, rep, index):
		super().__init__(bwd2, lod, rep, index)
		
		self.write_ddr = False       # Used by bzvdf_serializer
		self.write_target_r = False  #  
		self.write_target_u = False  #  
		self.write_target_f = False  #  
		self.write_time = False      # 
	
	def get_cockpit(self, raw=False):
		return self.bwd2.get_cockpit_object(self.index, raw)
	
	def get_lowpoly(self, raw=False):
		return self.bwd2.get_lowpoly_object(self.index, raw)

class SGeoObject(GeoObject):
	pass

class AnimObj:
	def __init__(self):
		self.name = ""
		self.animation_map = {}
		self.mesh_map = {}
		self.orientation_keyframe_list = []
		self.scale_keyframe_list = []
		self.position_keyframe_list = []
		
		# # # # # # # # # # # # # # # # # # #
		self._anim_ptr = 0                  # Unused!
		self._mesh_ptr = 0                  #
		self._orientation_keyframes_ptr = 0 # 
		self._scale_keyframes_ptr = 0       # 
		self._position_keyframes_ptr = 0 # 
		self._obj = 0                       # 
		self._entity = 0                    # 
	
	def create_animation(self, index):
		anim = Animation()
		anim.index = index
		self.animation_map[index] = anim
		return anim
	
	def animation_count(self):
		return len(self.animation_map)
	
	def animations(self):
		return self.animation_map.values()
	
	def create_animation_mesh(self, name):
		anim_mesh = AnimationMesh(self, name)
		self.mesh_map[name] = anim_mesh
		return anim_mesh
	
	def animation_mesh_count(self):
		return len(self.mesh_map)
	
	def animation_meshes(self):
		return self.mesh_map.values()
	
	def get_animation_mesh(self, name):
		if(name in self.mesh_map):
			return self.mesh_map[name]
		return None
	
	def animation_mesh_exists(self, name):
		return name in self.mesh_map
	
	def create_orientation_keyframe(self, frame, orientation):
		keyframe = OrientationKeyframe(frame, orientation)
		self.orientation_keyframe_list.append(keyframe)
		return keyframe
	
	def create_scale_keyframe(self, frame, scale):
		keyframe = ScaleKeyframe(frame, scale)
		self.scale_keyframe_list.append(keyframe)
		return keyframe
	
	def create_position_keyframe(self, frame, position):
		keyframe = PositionKeyframe(frame, position)
		self.position_keyframe_list.append(keyframe)
		return keyframe
	
	def slice_mesh_orientation_keyframes(self, mesh):
		return self.orientation_keyframe_list[mesh.orientation_start : mesh.orientation_start + mesh.orientation_length]
	
	def slice_mesh_scale_keyframes(self, mesh):
		return self.scale_keyframe_list[mesh.scale_start : mesh.scale_start + mesh.scale_length]
	
	def slice_mesh_position_keyframes(self, mesh):
		return self.position_keyframe_list[mesh.position_start : mesh.position_start + mesh.position_length]

class Animation:
	def __init__(self):
		self.index = 0     # Animation index is how the game selects its animations to play
		self.mesh_index_list = [0 for _ in range(32)]   # Unknown
		self.start = 0     # Starting frame of this animation on the timeline
		self.length = 0    # Signed frame count of this animation. Negative means reversed playback.
		self.loop = 0      # 0 = Infinite loop, 1+ = Play this many times
		self.speed = 0.0   # Frames per second playback rate
	
	def get_duration(self):
		return (abs(self.length) - 1) / self.speed

class AnimationMesh:
	def __init__(self, anim_obj, name=""):
		self.anim_obj = anim_obj
		self.name = name
		self.flags = 0
		self.inverse_transform = Transform()
		self.frame_transform = Transform()
		self.orientation_start = 0
		self.orientation_length = 0
		self.scale_start = 0
		self.scale_length = 0
		self.position_start = 0
		self.position_length = 0
	
	def get_positions(self):
		p_start = self.position_start
		p_end = p_start + self.position_length
		positions = self.anim_obj.position_keyframe_list[p_start : p_end]
		positions.sort(key=lambda kf: kf.frame)
		return positions
	
	def get_scales(self):
		s_start = self.scale_start
		s_end = s_start + self.scale_length
		scales = self.anim_obj.scale_keyframe_list[s_start : s_end]
		scales.sort(key=lambda kf: kf.frame)
		return scales
	
	def get_orientations(self):
		o_start = self.orientation_start
		o_end = o_start + self.orientation_length
		orientations = self.anim_obj.orientation_keyframe_list[o_start : o_end]
		orientations.sort(key=lambda kf: kf.frame)
		return orientations

class OrientationKeyframe:
	def __init__(self, frame, orientation):
		self.frame = frame
		self.orientation = orientation
	
	def __repr__(self):
		return(f"OrientationKeyframe({self.frame}, {self.orientation})")
	
	def __str__(self):
		return(f"{self.frame}: {self.orientation}")

class ScaleKeyframe:
	def __init__(self, frame, scale):
		self.frame = frame
		self.scale = scale
	
	def __repr__(self):
		return(f"ScaleKeyframe({self.frame}, {self.scale})")
	
	def __str__(self):
		return(f"{self.frame}: {self.scale}")

class PositionKeyframe:
	def __init__(self, frame, position):
		self.frame = frame
		self.position = position
	
	def __repr__(self):
		return(f"PositionKeyframe({self.frame}, {self.position})")
	
	def __str__(self):
		return(f"{self.frame}: {self.position}")

class BWD2:
	def __init__(self):
		self._revision = self.REVISION
		self.name = None
		self.entity_class = 0
		self.lod_dist_list = []
		self.objcount = 0
		self.object_list = [[[] for rep in range(self.GEO.REP.COUNT)] for lod in range(self.GEO.LOD.COUNT)]
		self.obj_namemap = {}
		self.obj_parentmap = {}
		
		self.anim_obj = None
	
	def get_end_object(self):
		return self.object_list[-1][-1][-1]
	
	def get_object(self, lod, rep, index, raw=False):
		geoobj = self.object_list[lod][rep][index]
		if(raw):
			return geoobj
		if(geoobj.is_null()):
			return None
		return geoobj
	
	def get_primary_object(self, index, raw=False):
		return self.get_object(self.GEO.LOD.PRIMARY, self.GEO.REP.PRIMARY, index, raw)
	
	def object_count(self):
		return self.objcount
	
	def geo_object_count(self):
		return len(tuple(self.all_geo_objects))
	
	def all_geo_objects(self, raw=False):
		for reps in self.object_list:
			for geoobjs in reps:
				for obj in geoobjs:
					if(not raw and obj.is_null()):
						continue
					yield obj
	
	def objects(self, lod, rep, raw=False):
		for obj in self.object_list[lod][rep]:
			if(not raw and obj.is_null()):
				continue
			yield obj
	
	def primary_objects(self, raw=False):
		return self.objects(self.GEO.LOD.PRIMARY, self.GEO.REP.PRIMARY, raw)
	
	def append_object(self):
		for lod, reps in enumerate(self.object_list):
			for rep, geoobjs in enumerate(reps):
				geoobjs.append(self.GeoObjectClass(self, lod, rep, len(geoobjs)))
		self.objcount += 1
	
	def insert_object(self, index):
		for lod, reps in enumerate(self.object_list):
			for rep, geoobjs in enumerate(reps):
				geoobjs.insert(index, self.GeoObjectClass(self, lod, rep, len(geoobjs)))
	
	def create_geo_object(self, lod, rep, index, name, parent):
		while(index >= self.objcount):
			self.append_object()
		obj = self.get_object(lod, rep, index, raw=True)
		obj.name = name
		obj.parent = parent
		if(name.lower() != 'null' and name.lower() != 'world'):
			self.obj_namemap[name] = obj
		return obj
	
	def get_object_by_name(self, name):
		# It's a bit more intricate when there's more than one object with the same name
		if(name in self.obj_namemap):
			return self.obj_namemap[name]
		else:
			return None
	
	def object_name_exists(self, name):
		if(name.lower() == 'null'):
			return False
		return name in self.obj_namemap
	
	def get_parent(self, obj):
		# TODO: I think this should go through the parent heirarchy in order, depth first, processing children before parents, taking the last matching object.
		if(obj.is_root()):
			return None
		return get_object_by_name(obj.parent)
	
	def get_primary_parent(self, obj):
		if(obj.lod != self.GEO.LOD.PRIMARY or obj.rep != self.GEO.REP.PRIMARY):
			obj = self.get_primary_object(obj.index)
		if(obj.is_root()):
			return None
		return get_object_by_name(obj.parent)
	

class VDF(BWD2):
	GEO = VGEO
	REVISION = VDF_REVISION
	GeoObjectClass = VGeoObject
	
	def __init__(self):
		super().__init__()
		self.entity_class = 0
		self.vehicle_size = 0
		self.lod_dist_list = []
		self.mass = 1750.0
		self.cdm = 1.0
		self.drag_coeff = 0.0008 # Shouldn't this be 0.01?
		self.hardpoint_count = 0    # unused
		
		self.collision_planes = None
		self.spcs_data = None
	
	def get_cockpit_object(self, index, raw=False):
		return self.get_object(self.GEO.LOD.COCKPIT, self.GEO.REP.PRIMARY, index, raw)
	
	def get_lowpoly_object(self, index, raw=False):
		return self.get_object(self.GEO.LOD.LOWPOLY, self.GEO.REP.PRIMARY, index, raw)
	
	def cockpit_objects(self, raw=False):
		return self.objects(self.GEO.LOD.COCKPIT, self.GEO.REP.PRIMARY, raw)
	
	def lowpoly_objects(self, raw=False):
		return self.objects(self.GEO.LOD.LOWPOLY, self.GEO.REP.PRIMARY, raw)

class SDF(BWD2):
	GEO = SGEO
	REVISION = VDF_REVISION
	GeoObjectClass = SGeoObject
	
	def __init__(self):
		super().__init__()
		self.struct_class = 0
		self.ddr = 0.0  # Type?
		self.death_animation = ""
		self.death_audio = ""
