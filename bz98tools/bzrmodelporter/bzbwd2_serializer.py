# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

# Chunk names:
#   BWD2 - WD2 might stand for World2
#   REV\0- Revision chunk, holds revision number
#   VDFC - Signifies vehicle data
#   VGEO - Holds vehicle geometry structure information
#   ANIM - Holds animations
#   VCHK - Unknown use (not in any stock VDF)
#   COLP - Collision planes used for physics collisions (not ordnance collisions though)
#   SPCS - Unknown use

# For some reason the redux does not care about the revision number.
# 1.5 will display "Bad BWD revision for file %s"

import itertools
from .bzbwd2 import (
	VDF, SDF,
	CollisionPlanes, AnimObj,
	VGEO, SGEO,
)
from .bz_baseserializer import (
	BZBaseSerializer,
	
	VECTOR3_SIZE, QUATERNION_SIZE,
	TRANSFORM_SIZE,
)

from .baseserializer import (
	UINT_SIZE, FLOAT_SIZE,
	AbruptEOFError,
)
CHUNK_HEADER_SIZE = 4 + UINT_SIZE

START_OF_STREAM = 0
CURRENT_STREAM_POSITION = 1



class BWD2BaseSerializer(BZBaseSerializer):
	def __init__(self, stream, endian='little'):
		super().__init__(stream, endian)
		self.current_chunk_addr = 0
		self.current_chunk_size = 0
	
	def read_chunk_header(self):
		self.current_chunk_addr = self.stream.tell()
		try:
			chunk_name = self.read_string(4)
		except(AbruptEOFError):
			raise
		except(EOFError):
			return None
		self.current_chunk_size = self.read_sint()
		
		return chunk_name
	
	def seek_next_chunk(self):
		self.stream.seek(self.current_chunk_addr + self.current_chunk_size, START_OF_STREAM)
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Read Methods
	
	def read_anim(self, anim_obj):
		anim_obj.name = self.read_string(16)
		animation_count = self.read_uint()
		mesh_count = self.read_uint()
		orientation_keyframe_count = self.read_uint()
		scale_keyframe_count = self.read_uint()
		position_keyframe_count = self.read_uint()
		anim_obj._anim_ptr = self.read_uint()
		anim_obj._mesh_ptr = self.read_uint()
		anim_obj._orientation_keyframe_ptr = self.read_uint()
		anim_obj._scale_keyframe_ptr = self.read_uint()
		anim_obj._position_keyframe_ptr = self.read_uint()
		anim_obj._obj = self.read_uint()
		anim_obj._entity = self.read_uint()
		
		# List of animations
		for i in range(animation_count):
			index = self.read_uint()
			animation = anim_obj.create_animation(index)
			animation.mesh_index_list[:] = self.read_uint_array(32)
			animation.start = self.read_uint()
			animation.length = self.read_sint()
			animation.loop = self.read_uint()
			animation.speed = self.read_float()
		
		# List of animation meshes
		for i in range(mesh_count):
			name = self.read_string(8)
			anim_mesh = anim_obj.create_animation_mesh(name)
			anim_mesh.flags = self.read_uint()
			anim_mesh.inverse_transform = self.read_transform()
			anim_mesh.frame_transform = self.read_transform()
			anim_mesh.orientation_start = self.read_uint()
			anim_mesh.orientation_length = self.read_uint()
			anim_mesh.scale_start = self.read_uint()
			anim_mesh.scale_length = self.read_uint()
			anim_mesh.position_start = self.read_uint()
			anim_mesh.position_length = self.read_uint()
		
		# Lists of keyframes
		for i in range(orientation_keyframe_count):
			frame = self.read_uint()
			orientation = self.read_quaternion()
			anim_obj.create_orientation_keyframe(frame, orientation)
		
		for i in range(scale_keyframe_count):
			frame = self.read_uint()
			scale = self.read_vector3()
			anim_obj.create_scale_keyframe(frame, scale)
		
		for i in range(position_keyframe_count):
			frame = self.read_uint()
			position = self.read_vector3()
			anim_obj.create_position_keyframe(frame, position)
		
		# Chunk validation
		end_addr = self.stream.tell()
		addr_delta = end_addr - self.current_chunk_addr
		if(addr_delta != self.current_chunk_size):
			print(f"ANIM chunk address delta ({addr_delta}) is different from given size ({self.current_chunk_size})! Ended read at address 0x{end_addr:X}")
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Write Methods
	
	def write_chunk_header(self, chunk_name, chunk_size):
		self.write_string(chunk_name, 4)
		self.write_sint(chunk_size)
	
	def write_exit(self):
		self.write_chunk_header('EXIT', CHUNK_HEADER_SIZE)
		
	def write_anim(self, anim_obj):
		self.write_chunk_header('ANIM', self.calc_anim_size(anim_obj))
		self.write_string(anim_obj.name, 16)
		self.write_uint(len(anim_obj.animation_map))
		self.write_uint(len(anim_obj.mesh_map))
		self.write_uint(len(anim_obj.orientation_keyframe_list))
		self.write_uint(len(anim_obj.scale_keyframe_list))
		self.write_uint(len(anim_obj.position_keyframe_list))
		self.write_uint(anim_obj._anim_ptr)
		self.write_uint(anim_obj._mesh_ptr)
		self.write_uint(anim_obj._orientation_keyframe_ptr)
		self.write_uint(anim_obj._scale_keyframe_ptr)
		self.write_uint(anim_obj._position_keyframe_ptr)
		self.write_uint(anim_obj._obj)
		self.write_uint(anim_obj._entity)
		
		self.write_animation_map(anim_obj.animation_map)
		self.write_mesh_map(anim_obj.mesh_map)
		self.write_animation_keyframe_lists(anim_obj)
	
	def write_animation_map(self, animation_map):
		for index, animation in animation_map.items():
			self.write_uint(index)
			self.write_uint_array(animation.mesh_index_list, 32)
			self.write_uint(animation.start)
			self.write_sint(animation.length)
			self.write_uint(animation.loop)
			self.write_float(animation.speed)
		
	def write_mesh_map(self, mesh_map):
		for name, animation_mesh in mesh_map.items():
			self.write_string(name, 8)
			self.write_uint(animation_mesh.flags)
			self.write_transform(animation_mesh.inverse_transform)
			self.write_transform(animation_mesh.frame_transform)
			self.write_uint(animation_mesh.orientation_start)
			self.write_uint(animation_mesh.orientation_length)
			self.write_uint(animation_mesh.scale_start)
			self.write_uint(animation_mesh.scale_length)
			self.write_uint(animation_mesh.position_start)
			self.write_uint(animation_mesh.position_length)
	
	def write_animation_keyframe_lists(self, anim_obj):
		for keyframe in anim_obj.orientation_keyframe_list:
			self.write_uint(keyframe.frame)
			self.write_quaternion(keyframe.orientation)
		
		for keyframe in anim_obj.scale_keyframe_list:
			self.write_uint(keyframe.frame)
			self.write_vector3(keyframe.scale)
		
		for keyframe in anim_obj.position_keyframe_list:
			self.write_uint(keyframe.frame)
			self.write_vector3(keyframe.position)
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Calc Methods
	
	def calc_animation_map_size(self, animation_map):
		return (
			UINT_SIZE      # animation index
			+ 32*UINT_SIZE # mesh index list
			+ UINT_SIZE    # start
			+ UINT_SIZE    # length
			+ UINT_SIZE    # loop
			+ FLOAT_SIZE   # speed
		) * len(animation_map)
	
	def calc_mesh_map_size(self, mesh_map):
		return (
			8                # name
			+ UINT_SIZE      # flags
			+ TRANSFORM_SIZE # inverse transform
			+ TRANSFORM_SIZE # frame transform
			+ UINT_SIZE      # orientation start
			+ UINT_SIZE      # orientation length
			+ UINT_SIZE      # scale start
			+ UINT_SIZE      # scale length
			+ UINT_SIZE      # position start
			+ UINT_SIZE      # position length
		) * len(mesh_map)
	
	def calc_animation_keyframe_lists_size(self, anim_obj):
		return (
			(
				UINT_SIZE         # frame
				+ QUATERNION_SIZE # orientation
			) * len(anim_obj.orientation_keyframe_list)
			+ (
				UINT_SIZE      # frame
				+ VECTOR3_SIZE # scale
			) * len(anim_obj.scale_keyframe_list)
			+ (
				UINT_SIZE      # frame
				+ VECTOR3_SIZE # position
			) * len(anim_obj.position_keyframe_list)
		)
		
	def calc_anim_size(self, anim_obj):
		return (CHUNK_HEADER_SIZE
			+ 16    # name
			+ UINT_SIZE # animation count
			+ UINT_SIZE # animation mesh count
			+ UINT_SIZE # orientation keyframe count
			+ UINT_SIZE # scale keyframe count
			+ UINT_SIZE # position keyframe count
			+ 7*UINT_SIZE # animPtr, meshPtr, rotKeyPtr, sclKeyPtr, posKeyPtr, obj, entity
			+ self.calc_animation_map_size(anim_obj.animation_map)
			+ self.calc_mesh_map_size(anim_obj.mesh_map)
			+ self.calc_animation_keyframe_lists_size(anim_obj)
		)

class VDFSerializer(BWD2BaseSerializer):
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Read Methods
	
	def read(self, vdf=None):
		if(vdf is None):
			vdf = VDF()
		
		# Read header chunks
		chunk_name = self.read_chunk_header()
		if(chunk_name != "BWD2"):
			raise Exception(f"Expected chunk BWD2 at address {self.current_chunk_addr}; got \"{chunk_name}\"!")
		self.seek_next_chunk()
		chunk_name = self.read_chunk_header()  # REV\0  - no need to check chunk name
		vdf._revision = self.read_uint()
		self.seek_next_chunk()
		
		# Read the rest of the VDF
		chunk_name = self.read_chunk_header()
		if(chunk_name == "VDFC"):
			self.read_vdfc(vdf)
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
		
		for _ in range(3):
			if(chunk_name == "EXIT"):
				self.seek_next_chunk()
				chunk_name = self.read_chunk_header()
			else:
				break
		if(chunk_name == "VGEO"):
			self.read_vgeo(vdf)
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
			
		if(chunk_name == "ANIM"):
			anim_obj = AnimObj()
			vdf.anim_obj = anim_obj
			self.read_anim(anim_obj)
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
			
		if(chunk_name == "VCHK"):
			self.read_vchk(vdf)
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
		
		for _ in range(2):
			if(chunk_name == "EXIT"):
				self.seek_next_chunk()
				chunk_name = self.read_chunk_header()
			else:
				break
			
		if(chunk_name == "COLP"):
			colp = CollisionPlanes()
			vdf.collision_planes = colp
			self.read_colp(colp)
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
		
		if(chunk_name == "EXIT"):     # Unknown how many EXIT chunks are acceptable here
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
			
		if(chunk_name == "SPCS"):
			self.read_spcs(vdf)
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
		
		for _ in range(2):            # Unknown how many EXIT chunks are acceptable here
			if(chunk_name == "EXIT"):
				self.seek_next_chunk()
				chunk_name = self.read_chunk_header()
			else:
				break
		
		return vdf
	
	def read_vdfc(self, vdf):
		vdf.name = self.read_string(16)
		vdf.entity_class = self.read_uint()
		vdf.vehicle_size = self.read_uint()
		vdf.lod_dist_list[:] = self.read_float_array(5)
		vdf.mass = self.read_float()
		vdf.cdm = self.read_float()
		vdf.drag_coeff = self.read_float()
		vdf.hardpoint_count = self.read_uint()    # unused
	
	def read_vgeo(self, vdf):
		geo_count = self.read_uint()
		
		for lod, rep, index in itertools.product(range(VGEO.LOD.COUNT), range(VGEO.REP.COUNT), range(geo_count)):
			name = self.read_string(8)
			transform = self.read_transform()
			parent = self.read_string(8)
			
			geo_object = vdf.create_geo_object(lod, rep, index, name, parent)
			geo_object.transform = transform
			
			geo_object.center_pos = self.read_vector3()
			geo_object.radius = self.read_float()
			geo_object.half_size = self.read_vector3()
			geo_object.class_id = self.read_uint()
			geo_object.object_flags = self.read_uint()
			
			# # # # # # # # # # # # # # # #
			geo_object.ddr = self.read_uint()             # ddr, unknown type (what is this?)
			geo_object.target = self.read_vector3()       # When the object is a spinner, this is the angular velocity divided by 2*pi
			geo_object.time = self.read_float()           # Purpose unknown. Maybe an I76 holdover?
			self.stream.seek(-20, CURRENT_STREAM_POSITION)     # UINT_SIZE + VECTOR3_SIZE + FLOAT_SIZE = 4 + 12 + 4 = 20
	
	def read_vchk(self, vdf):
		pass # Unknown
	
	def read_colp(self, colp):
		colp.front = self.read_float()
		colp.front_middle = self.read_float()
		colp.back_middle = self.read_float()
		colp.back = self.read_float()
		colp.right = self.read_float()
		colp.right_middle = self.read_float()
		colp.left_middle = self.read_float()
		colp.left = self.read_float()
		colp.top = self.read_float()
		colp.top_middle = self.read_float()
		colp.bottom_middle = self.read_float()
		colp.bottom = self.read_float()
	
	def read_spcs(self, vdf):
		vdf.spcs_data = self.read_uint_array(3)
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Write Methods
	
	def write(self, vdf):
		# Write header
		self.write_chunk_header('BWD2', CHUNK_HEADER_SIZE)
		self.write_chunk_header('REV', CHUNK_HEADER_SIZE + UINT_SIZE) # revision
		self.write_uint(vdf._revision)
		
		# Write rest of VDF
		self.write_vdfc(vdf)
		self.write_exit()
		self.write_vgeo(vdf)
		if(vdf.anim_obj is not None):
			self.write_anim(vdf.anim_obj)
		self.write_exit()
		self.write_exit()
		if(vdf.collision_planes is not None):
			self.write_colp(vdf.collision_planes)
		self.write_exit()
		if(vdf.spcs_data is not None):
			self.write_spcs(vdf)
		self.write_exit()
	
	def write_vdfc(self, vdf):
		self.write_chunk_header('VDFC', self.calc_vdfc_size())
		self.write_string(vdf.name, 16)
		self.write_uint(vdf.entity_class)             # unused?
		self.write_uint(vdf.vehicle_size)             # unused?
		self.write_float_array(vdf.lod_dist_list, 5)  # unused?
		self.write_float(vdf.mass)
		self.write_float(vdf.cdm)
		self.write_float(vdf.drag_coeff)
		self.write_uint(vdf.hardpoint_count)          # unused
	
	def write_vgeo(self, vdf):
		self.write_chunk_header('VGEO', self.calc_vgeo_size(vdf))
		self.write_uint(vdf.objcount)
		prev_geo_object = None
		for geo_object in vdf.all_geo_objects(raw=True):
			start_addr = self.stream.tell()
			self.write_string(geo_object.name, 8)
			self.write_transform(geo_object.transform)
			self.write_string(geo_object.parent, 8)
			self.write_vector3(geo_object.center_pos)
			self.write_float(geo_object.radius)
			self.write_vector3(geo_object.half_size)
			self.write_uint(geo_object.class_id)
			self.write_uint(geo_object.object_flags)
			
			if(prev_geo_object is not None and (
				prev_geo_object.write_ddr
				or prev_geo_object.write_target_r
				or prev_geo_object.write_target_u
				or prev_geo_object.write_target_f
				or prev_geo_object.write_time
			)):
				end_addr = self.stream.tell()
				self.stream.seek(start_addr, START_OF_STREAM)
				if(prev_geo_object.write_ddr):
					self.write_uint(prev_geo_object.ddr)
				else:
					self.stream.seek(UINT_SIZE, CURRENT_STREAM_POSITION)
				
				if(prev_geo_object.write_target_r):
					self.write_float(prev_geo_object.target.r)
				else:
					self.stream.seek(FLOAT_SIZE, CURRENT_STREAM_POSITION)
				
				if(prev_geo_object.write_target_u):
					self.write_float(prev_geo_object.target.u)
				else:
					self.stream.seek(FLOAT_SIZE, CURRENT_STREAM_POSITION)
				
				if(prev_geo_object.write_target_f):
					self.write_float(prev_geo_object.target.f)
				else:
					self.stream.seek(FLOAT_SIZE, CURRENT_STREAM_POSITION)
				
				if(prev_geo_object.write_time):
					self.write_float(prev_geo_object.time)
				
				self.stream.seek(end_addr, START_OF_STREAM)
			prev_geo_object = geo_object
		
		count = 0
		if(prev_geo_object is not None):
			if(prev_geo_object.write_time):
				count = 5
			elif(prev_geo_object.write_target_f):
				count = 4
			elif(prev_geo_object.write_target_u):
				count = 3
			elif(prev_geo_object.write_target_r):
				count = 2
			elif(prev_geo_object.write_ddr):
				count = 1
			
		if(count > 0):
			if(count >= 1):
				if(prev_geo_object.write_time):
					self.write_uint(prev_geo_object.ddr)
				else:
					self.write_uint(0)
			
			if(count >= 2):
				if(prev_geo_object.write_target_r):
					self.write_uint(prev_geo_object.target.r)
				else:
					self.write_float(0)
			
			if(count >= 3):
				if(prev_geo_object.write_target_u):
					self.write_uint(prev_geo_object.target.u)
				else:
					self.write_float(0)
			
			if(count >= 4):
				if(prev_geo_object.write_target_f):
					self.write_uint(prev_geo_object.target.f)
				else:
					self.write_float(0)
			
			if(count >= 5):
				if(prev_geo_object.write_time):
					self.write_float(prev_geo_object.time)
				else:
					self.write_float(0)
	
	def write_colp(self, colp):
		self.write_chunk_header('COLP', self.calc_colp_size())
		self.write_float(colp.front)
		self.write_float(colp.front_middle)
		self.write_float(colp.back_middle)
		self.write_float(colp.back)
		self.write_float(colp.right)
		self.write_float(colp.right_middle)
		self.write_float(colp.left_middle)
		self.write_float(colp.left)
		self.write_float(colp.top)
		self.write_float(colp.top_middle)
		self.write_float(colp.bottom_middle)
		self.write_float(colp.bottom)
	
	def write_spcs(self, vdf):
		self.write_chunk_header('SPCS', self.calc_spcs_size())
		self.write_uint_array(vdf.spcs_data, 3)
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Calc Methods
	
	def calc_vdfc_size(self):
		return (CHUNK_HEADER_SIZE
			+ 16           # name
			+ UINT_SIZE    # entity_class
			+ UINT_SIZE    # vehicle_size
			+ 5*FLOAT_SIZE # lod_dist_list
			+ FLOAT_SIZE   # mass
			+ FLOAT_SIZE   # cdm
			+ FLOAT_SIZE   # drag_coeff
			+ UINT_SIZE    # hardpoint_count
		)
	
	def calc_vgeo_size(self, vdf):
		extra = 0
		if(vdf.objcount > 0):
			geo_object = vdf.get_end_object()
			if(geo_object.write_time):
				extra = 5 * 4
			elif(geo_object.write_target_f):
				extra = 4 * 4
			elif(geo_object.write_target_u):
				extra = 3 * 4
			elif(geo_object.write_target_r):
				extra = 2 * 4
			elif(geo_object.write_ddr):
				extra = 1 * 4
		
		return (CHUNK_HEADER_SIZE + UINT_SIZE # geo element count
			+ ( 8                 # name
				+ TRANSFORM_SIZE  # transform
				+ 8               # parent
				+ VECTOR3_SIZE    # center_pos
				+ FLOAT_SIZE      # radius
				+ VECTOR3_SIZE    # half_size
				+ UINT_SIZE       # class_id
				+ UINT_SIZE       # object_flags
			) * VGEO.LOD.COUNT * VGEO.REP.COUNT * vdf.objcount
			+ extra
		)
	
	def calc_colp_size(self):
		return (CHUNK_HEADER_SIZE
			+ FLOAT_SIZE # front
			+ FLOAT_SIZE # front mid
			+ FLOAT_SIZE # back mid
			+ FLOAT_SIZE # back
			+ FLOAT_SIZE # right
			+ FLOAT_SIZE # right mid
			+ FLOAT_SIZE # left mid
			+ FLOAT_SIZE # left
			+ FLOAT_SIZE # top
			+ FLOAT_SIZE # top mid
			+ FLOAT_SIZE # bottom mid
			+ FLOAT_SIZE # bottom
		)
	
	def calc_spcs_size(self):
		return (CHUNK_HEADER_SIZE
			+ 12  # Unknown 12 bytes / 3 words.
		)


class SDFSerializer(BWD2BaseSerializer):
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Read Methods
	
	def read(self, sdf=None):
		if(sdf is None):
			sdf = SDF()
		
		# Read header chunks
		chunk_name = self.read_chunk_header()
		if(chunk_name != "BWD2"):
			raise Exception(f"Expected chunk BWD2 at address {self.current_chunk_addr}; got \"{chunk_name}\"!")
		self.seek_next_chunk()
		chunk_name = self.read_chunk_header()  # REV\0  - no need to check chunk name
		sdf._revision = self.read_uint()
		self.seek_next_chunk()
		
		# Read the rest of the SDF
		chunk_name = self.read_chunk_header()
		if(chunk_name == "SDFC"):
			self.read_sdfc(sdf)
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
		
		for _ in range(3):
			if(chunk_name == "EXIT"):
				self.seek_next_chunk()
				chunk_name = self.read_chunk_header()
			else:
				break
		
		if(chunk_name == "SGEO"):
			self.read_sgeo(sdf)
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
			
		if(chunk_name == "ANIM"):
			anim_obj = AnimObj()
			sdf.anim_obj = anim_obj
			self.read_anim(anim_obj)
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
		
		for _ in range(2):
			if(chunk_name == "EXIT"):
				self.seek_next_chunk()
				chunk_name = self.read_chunk_header()
			else:
				break
		
		if(chunk_name == "EXIT"):     # Unknown how many EXIT chunks are acceptable here
			self.seek_next_chunk()
			chunk_name = self.read_chunk_header()
		
		for _ in range(2):            # Unknown how many EXIT chunks are acceptable here
			if(chunk_name == "EXIT"):
				self.seek_next_chunk()
				chunk_name = self.read_chunk_header()
			else:
				break
		
		return sdf
		
	def read_sdfc(self, sdf):
		sdf.name = self.read_string(16)
		sdf.struct_class = self.read_uint()
		sdf.lod_dist_list[:] = self.read_float_array(5)
		sdf.ddr = self.read_uint()  # Type?
		sdf.death_animation = self.read_string(13)
		sdf.death_audio = self.read_string(13)
	
	def read_sgeo(self, sdf):
		geo_count = self.read_uint()
		
		for lod, rep, index in itertools.product(range(SGEO.LOD.COUNT), range(SGEO.REP.COUNT), range(geo_count)):
			name = self.read_string(8)
			transform = self.read_transform()
			parent = self.read_string(8)
			
			geo_object = sdf.create_geo_object(lod, rep, index, name, parent)
			geo_object.transform = transform
			
			geo_object.center_pos = self.read_vector3()
			geo_object.radius = self.read_float()
			geo_object.half_size = self.read_vector3()
			geo_object.class_id = self.read_uint()
			geo_object.object_flags = self.read_uint()
			geo_object.ddr = self.read_uint()       # ddr, unknown type (what is this?)
			geo_object.target = self.read_vector3() # When the object is a spinner, this is the angular velocity divided by 2*pi
			geo_object.time = self.read_float()     # Purpose unknown. Maybe an I76 holdover?
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Write Methods
	
	def write(self, sdf):
		# Write header
		self.write_chunk_header('BWD2', CHUNK_HEADER_SIZE)
		self.write_chunk_header('REV', CHUNK_HEADER_SIZE + UINT_SIZE) # revision
		self.write_uint(sdf._revision)
		
		# Write rest of SDF
		self.write_sdfc(sdf)
		self.write_sgeo(sdf)
		if(sdf.anim_obj is not None):
			self.write_anim(sdf.anim_obj)
		self.write_exit()
		self.write_exit()
		self.write_exit()
	
	def write_sdfc(self, sdf):
		self.write_chunk_header('SDFC', self.calc_sdfc_size())
		self.write_string(sdf.name, 16)
		self.write_uint(sdf.struct_class)             # unused?
		self.write_float_array(sdf.lod_dist_list, 5)  # unused?
		self.write_uint(sdf.ddr)
		self.write_string(sdf.death_animation, 13)
		self.write_string(sdf.death_audio, 13)
		
	def write_sgeo(self, sdf):
		self.write_chunk_header('SGEO', self.calc_sgeo_size(sdf))
		self.write_uint(sdf.objcount)
		for lod, rep, index in itertools.product(range(SGEO.LOD.COUNT), range(SGEO.REP.COUNT), range(sdf.objcount)):
			geo_object = sdf.get_object(lod, rep, index, raw=True)
			self.write_string(geo_object.name, 8)
			self.write_transform(geo_object.transform)
			self.write_string(geo_object.parent, 8)
			self.write_vector3(geo_object.center_pos)
			self.write_float(geo_object.radius)
			self.write_vector3(geo_object.half_size)
			self.write_uint(geo_object.class_id)
			self.write_uint(geo_object.object_flags)
			self.write_uint(geo_object.ddr)
			self.write_vector3(geo_object.target)
			self.write_float(geo_object.time)
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Calc Methods
	
	def calc_sdfc_size(self):
		return (CHUNK_HEADER_SIZE
			+ 16           # name
			+ UINT_SIZE    # struct_class
			+ 5*FLOAT_SIZE # lod_dist_list
			+ UINT_SIZE    # ddr
			+ 13           # death_animation
			+ 13           # death_sound
		)
	
	def calc_sgeo_size(self, sdf):
		return (CHUNK_HEADER_SIZE + UINT_SIZE # geo element count
			+ ( 8                 # name
				+ TRANSFORM_SIZE  # transform
				+ 8               # parent
				+ VECTOR3_SIZE    # center_pos
				+ FLOAT_SIZE      # radius
				+ VECTOR3_SIZE    # half_size
				+ UINT_SIZE       # class_id
				+ UINT_SIZE       # object_flags
				+ UINT_SIZE       # ddr
				+ VECTOR3_SIZE    # target
				+ FLOAT_SIZE      # time
			) * SGEO.LOD.COUNT * SGEO.REP.COUNT * sdf.objcount
		)