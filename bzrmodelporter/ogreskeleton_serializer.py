from .ogreskeleton import Skeleton

from .baseserializer import (
	USHORT_SIZE, FLOAT_SIZE,
	VECTOR3_SIZE, QUATERNION_SIZE,
)

from .ogre_baseserializer import (
	OgreBaseSerializer,
	CHUNK_HEADER_SIZE,
	UnsupportedVersionError,
)

BLENDMODE_SIZE = (
	CHUNK_HEADER_SIZE
	+ USHORT_SIZE   # blendmode
)
BONE_PARENT_SIZE = (
	CHUNK_HEADER_SIZE
	+ USHORT_SIZE                        # bone handle
	+ USHORT_SIZE                        # parent handle
)
BONE_SIZE_WITHOUT_SCALE = (
	CHUNK_HEADER_SIZE
#   + calc_string_size(bone.name)  # name  -  Actually ignored by the chunk size attribute!
	+ USHORT_SIZE                  # handle
	+ VECTOR3_SIZE                 # position
	+ QUATERNION_SIZE              # orientation
)
KEYFRAME_SIZE_WITHOUT_SCALE = (
	CHUNK_HEADER_SIZE
	+ FLOAT_SIZE                    # time
	+ QUATERNION_SIZE               # rotation
	+ VECTOR3_SIZE                  # translation
)
		
START_OF_STREAM = 0
CURRENT_STREAM_POSITION = 1
END_OF_STREAM = 2

class SkeletonChunkID:
	SKELETON_HEADER                   = 0x1000
	SKELETON_BLENDMODE                = 0x1010
	
	SKELETON_BONE                     = 0x2000
	
	SKELETON_BONE_PARENT              = 0x3000
	
	SKELETON_ANIMATION                = 0x4000
	SKELETON_ANIMATION_BASEINFO       = 0x4010
	SKELETON_ANIMATION_TRACK          = 0x4100
	SKELETON_ANIMATION_TRACK_KEYFRAME = 0x4110
	
	SKELETON_ANIMATION_LINK           = 0x5000
	
	name_map = {
		SKELETON_HEADER:                   "SKELETON_HEADER",
		SKELETON_BLENDMODE:                "SKELETON_BLENDMODE",
		
		SKELETON_BONE:                     "SKELETON_BONE",
		
		SKELETON_BONE_PARENT:              "SKELETON_BONE_PARENT",
		
		SKELETON_ANIMATION:                "SKELETON_ANIMATION",
		SKELETON_ANIMATION_BASEINFO:       "SKELETON_ANIMATION_BASEINFO",
		SKELETON_ANIMATION_TRACK:          "SKELETON_ANIMATION_TRACK",
		SKELETON_ANIMATION_TRACK_KEYFRAME: "SKELETON_ANIMATION_TRACK_KEYFRAME",
		
		SKELETON_ANIMATION_LINK:           "SKELETON_ANIMATION_LINK",
	}
	
	@staticmethod
	def label(id, full=False):
		if(id in SkeletonChunkID.name_map):
			if(full):
				return f"{SkeletonChunkID.name_map[id]}[0x{id:4X}]"
			else:
				return SkeletonChunkID.name_map[id]
		else:
			return f"SkeletonChunkID[0x{id:4X}]"
	
	@staticmethod
	def isvalid(id):
		return id in SkeletonChunkID.name_map

class SkeletonAnimationBlendMode:
	ANIMBLEND_AVERAGE    = 0x0000 # Animations are applied by calculating a weighted average of all animations.
	ANIMBLEND_CUMULATIVE = 0x0001 # Animations are applied by calculating a weighted cumulative total.
	
	name_map = {
		"ANIMBLEND_AVERAGE":    ANIMBLEND_AVERAGE,
		"ANIMBLEND_CUMULATIVE": ANIMBLEND_CUMULATIVE,
	}
	
	@staticmethod
	def label(blendmode, full=False):
		if(blendmode in SkeletonAnimationBlendMode.name_map):
			if(full):
				return f"{SkeletonAnimationBlendMode.name_map[blendmode]}[0x{blendmode:4X}]"
			else:
				return SkeletonAnimationBlendMode.name_map[blendmode]
		else:
			return f"SkeletonAnimationBlendMode[0x{blendmode:4X}]"
	
	@staticmethod
	def isvalid(blendmode):
		return blendmode in SkeletonAnimationBlendMode.name_map

class SkeletonSerializer(OgreBaseSerializer):
	ChunkID = SkeletonChunkID
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Read Methods
	
	def read(self, skeleton=None):
		if(skeleton is None):
			skeleton = Skeleton()
		self.read_file_header()
		while(True):
			try:
				chunk_id = self.read_chunk_header()
			except(EOFError):
				break
				
			if(chunk_id == SkeletonChunkID.SKELETON_BLENDMODE):
				self.read_blendmode(skeleton)
				
			elif(chunk_id == SkeletonChunkID.SKELETON_BONE):
				self.read_bone(skeleton)
				
			elif(chunk_id == SkeletonChunkID.SKELETON_BONE_PARENT):
				self.read_bone_parent(skeleton)
				
			elif(chunk_id == SkeletonChunkID.SKELETON_ANIMATION):
				self.read_animation(skeleton)
				
			elif(chunk_id == SkeletonChunkID.SKELETON_ANIMATION_LINK):
				self.read_animation_link(skeleton)
				
			else:
				break
		return skeleton
	
	def read_file_header(self):
		header_id = self.read_raw(2)
		if(header_id == b"\x00\x10"):
			self.endian = 'little'
		elif(header_id == b"\x10\x00"):
			self.endian = 'big'
		else:
			raise Exception(f"Invalid header id {header_id}")
		
		self.version = self.read_string()
		if(self.version not in {
			'[Serializer_v1.80]',
			'[Serializer_v1.10]',
		}):
			raise UnsupportedVersionError(f"Unsupported skeleton file version {self.version}")
	
	def read_blendmode(self, skeleton):
		skeleton.blendmode = self.read_ushort()
		self.pop_chunk(SkeletonChunkID.SKELETON_BLENDMODE)
	
	def read_bone(self, skeleton):
		self.start_ignore_chunk()
		name = self.read_string()
		self.stop_ignore_chunk()
		handle = self.read_ushort()
		pos = self.read_vector3()
		ori = self.read_quaternion()
		if(self.current_chunk_size() > BONE_SIZE_WITHOUT_SCALE):
			scale = self.read_vector3()
		else:
			scale = None
		
		bone = skeleton.create_bone(name, handle, pos, ori, scale)
		self.pop_chunk(SkeletonChunkID.SKELETON_BONE)
	
	def read_bone_parent(self, skeleton):
		handle = self.read_ushort()
		parent_handle = self.read_ushort()
		
		bone = skeleton.get_bone(handle)
		parent_bone = skeleton.get_bone(parent_handle)
		parent_bone.add_child(bone)
		self.pop_chunk(SkeletonChunkID.SKELETON_BONE_PARENT)
	
	def read_animation(self, skeleton):
		#self.start_ignore_chunk()
		name = self.read_string()
		#self.stop_ignore_chunk()
		duration = self.read_float()
		
		animation = skeleton.create_animation(name, duration)
		
		try:
			chunk_id = self.read_chunk_header()
		except(EOFError):
			return
		if(chunk_id == SkeletonChunkID.SKELETON_ANIMATION_BASEINFO):
			animation._use_base_keyframe = True
			animation.base_keyframe_animation_name = self.read_string()
			animation.base_keyframe_time = self.read_float()
			self.pop_chunk(SkeletonChunkID.SKELETON_ANIMATION_BASEINFO)
		else:
			self.rollback_chunk_header()
		
		while(True):
			try:
				chunk_id = self.read_chunk_header()
			except(EOFError):
				break
			if(chunk_id == SkeletonChunkID.SKELETON_ANIMATION_TRACK):  
				self.read_animation_track(skeleton, animation)
			else:
				self.rollback_chunk_header()
				break
		self.pop_chunk(SkeletonChunkID.SKELETON_ANIMATION)
		
	def read_animation_track(self, skeleton, animation):
		handle = self.read_ushort()
		
		bone = skeleton.get_bone(handle)
		track = animation.create_track(bone)
		while(True):
			try:
				chunk_id = self.read_chunk_header()
			except(EOFError):
				break
			if(chunk_id == SkeletonChunkID.SKELETON_ANIMATION_TRACK_KEYFRAME):
				self.read_animation_track_keyframe(track)
			else:
				self.rollback_chunk_header()
				break
		self.pop_chunk(SkeletonChunkID.SKELETON_ANIMATION_TRACK)
	
	def read_animation_track_keyframe(self, track):
		time = self.read_float()
		
		keyframe = track.create_keyframe(time)
		keyframe.rotation = self.read_quaternion()
		keyframe.translation = self.read_vector3()
		if(self.current_chunk_size() > KEYFRAME_SIZE_WITHOUT_SCALE):
			keyframe.scale = self.read_vector3()
		self.pop_chunk(SkeletonChunkID.SKELETON_ANIMATION_TRACK_KEYFRAME)
	
	def read_animation_link(self, skeleton):
		skeleton_name = self.read_string()
		scale = self.read_float()
		skeleton.create_linked_skeleton_animation_source(skeleton_name, scale)
		self.pop_chunk(SkeletonChunkID.SKELETON_ANIMATION_LINK)
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Write Methods
	
	def write(self, skeleton, version='[Serializer_v1.80]'):
		self.version = version
		if(self.version not in {'[Serializer_v1.80]'}):
			raise UnsupportedVersionError(f"Version {self.version} does not currently have write support!")
		self.write_file_header()
		
		if(self.version == '[Serializer_v1.80]'):
			self.write_blendmode(skeleton)
		for bone in skeleton.bones():
			self.write_bone(bone)
		for bone in skeleton.bones():
			if(bone.parent is not None):
				self.write_bone_parent(bone)
		
		for animation in skeleton.animations():
			self.write_animation(animation)
		
		for lsas in skeleton.sources():
			self.write_skeleton_animation_link(lsas)
		
		if(self.validate_chunk_sizes and self.are_chunks_remaining()):
			print(f"WARNING: {len(self.chunk_stack)} chunks still remain in the chunk stack!")
			print(self.chunk_stack)
		
	def write_file_header(self):
		self.write_ushort(SkeletonChunkID.SKELETON_HEADER)
		self.write_string(self.version)
	
	def write_blendmode(self, skeleton):
		self.write_chunk_header(SkeletonChunkID.SKELETON_BLENDMODE, BLENDMODE_SIZE)
		self.write_ushort(skeleton.blendmode)     # blendmode
		self.pop_chunk(SkeletonChunkID.SKELETON_BLENDMODE)
	
	def write_bone(self, bone):
		size = self.calc_bone_size(bone)
		self.write_chunk_header(SkeletonChunkID.SKELETON_BONE, size)
		self.start_ignore_chunk()
		self.write_string(bone.name)              # name
		self.stop_ignore_chunk()
		self.write_ushort(bone.handle)            # handle
		self.write_vector3(bone.position)         # position
		self.write_quaternion(bone.orientation)   # orientation
		if(bone.scale is not None and (
			bone.scale.x != 1.0 
			or bone.scale.y != 1.0 
			or bone.scale.z != 1.0
		)):
			self.write_vector3(bone.scale)         # scale
		self.pop_chunk(SkeletonChunkID.SKELETON_BONE)
	
	def write_bone_parent(self, bone):
		self.write_chunk_header(SkeletonChunkID.SKELETON_BONE_PARENT, BONE_PARENT_SIZE)
		self.write_ushort(bone.handle)
		self.write_ushort(bone.parent.handle)
		self.pop_chunk(SkeletonChunkID.SKELETON_BONE_PARENT)
		
	def write_animation(self, animation):
		size = self.calc_animation_size(animation)
		self.write_chunk_header(SkeletonChunkID.SKELETON_ANIMATION, size)
		self.write_string(animation.name)         # name
		self.write_float(animation.duration)      # duration
		if(self.version == '[Serializer_v1.80]' and animation.use_base_keyframe):
			self.write_animation_baseinfo(animation)
		for track in animation.track_map.values():
			self.write_animation_track(track)
		self.pop_chunk(SkeletonChunkID.SKELETON_ANIMATION)
	
	def write_animation_baseinfo(self, animation):
		size = self.calc_animation_baseinfo_size(animation)
		self.write_chunk_header(SkeletonChunkID.SKELETON_ANIMATION_BASEINFO, size)
		self.write_string(animation.base_keyframe_animation_name)
		self.write_float(animation.base_keyframe_time)
		self.pop_chunk(SkeletonChunkID.SKELETON_ANIMATION_BASEINFO)
		
	def write_animation_track(self, track):
		size = self.calc_animation_track_size(track)
		self.write_chunk_header(SkeletonChunkID.SKELETON_ANIMATION_TRACK, size)
		self.write_ushort(track.target_bone.handle)
		for keyframe in track.keyframe_list:
			self.write_animation_track_keyframe(keyframe)
		self.pop_chunk(SkeletonChunkID.SKELETON_ANIMATION_TRACK)
	
	def write_animation_track_keyframe(self, keyframe):
		size = self.calc_animation_track_keyframe_size(keyframe)
		self.write_chunk_header(SkeletonChunkID.SKELETON_ANIMATION_TRACK_KEYFRAME, size)
		self.write_float(keyframe.time)                # time
		self.write_quaternion(keyframe.rotation)       # rotation
		self.write_vector3(keyframe.translation)       # translation
		if(keyframe.scale is not None and (
			keyframe.scale.x != 1.0 
			or keyframe.scale.y != 1.0 
			or keyframe.scale.z != 1.0
		)):
			self.write_vector3(keyframe.scale)         # scale
		self.pop_chunk(SkeletonChunkID.SKELETON_ANIMATION_TRACK_KEYFRAME)
		
	def write_skeleton_animation_link(self, lsas):
		size = self.calc_animation_link_size(lsas)
		self.write_chunk_header(SkeletonChunkID.SKELETON_ANIMATION_LINK, size)
		self.write_string(lsas.skeleton_name)
		self.write_float(lsas.scale)
		self.pop_chunk(SkeletonChunkID.SKELETON_ANIMATION_LINK)
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Calc Methods
	
	def calc_bone_size(self, bone):
		# SKELETON_BONE
		if(bone.scale is not None and (
			bone.scale.x != 1.0 
			or bone.scale.y != 1.0 
			or bone.scale.z != 1.0
		)):
			return (
				BONE_SIZE_WITHOUT_SCALE
				+ VECTOR3_SIZE                 # scale
			)
		return BONE_SIZE_WITHOUT_SCALE
	
	def calc_animation_size(self, animation):
		# SKELETON_ANIMATION
		size = (CHUNK_HEADER_SIZE
			+ self.calc_string_size(animation.name)   # name
			+ FLOAT_SIZE                              # duration
		)
		if(self.version == '[Serializer_v1.80]' and animation.use_base_keyframe):
			size += self.calc_animation_baseinfo_size(animation)   # SKELETON_ANIMATION_BASEINFO
		for track in animation.track_map.values():
			size += self.calc_animation_track_size(track)          # SKELETON_ANIMATION_TRACK
		return size
	
	def calc_animation_baseinfo_size(self, animation):
		# SKELETON_ANIMATION_BASEINFO
		return (CHUNK_HEADER_SIZE
			+ self.calc_string_size(animation.base_keyframe_animation_name)   # name
			+ FLOAT_SIZE                                                      # duration
		)
	
	def calc_animation_track_size(self, track):
		# SKELETON_ANIMATION_TRACK
		size = (CHUNK_HEADER_SIZE
			+ USHORT_SIZE                       # bone index
		)
		for keyframe in track.keyframe_list:
			size += self.calc_animation_track_keyframe_size(keyframe)
		return size
	
	def calc_animation_track_keyframe_size(self, keyframe):
		# SKELETON_ANIMATION_TRACK_KEYFRAME
		if(keyframe.scale is not None and (
			keyframe.scale.x != 1.0 
			or keyframe.scale.y != 1.0 
			or keyframe.scale.z != 1.0
		)):
			return (
				KEYFRAME_SIZE_WITHOUT_SCALE
				+ VECTOR3_SIZE                # scale
			)
		return KEYFRAME_SIZE_WITHOUT_SCALE
	
	def calc_animation_link_size(self, lsas):
		# SKELETON_ANIMATION_LINK
		return (CHUNK_HEADER_SIZE
			+ self.calc_string_size(lsas.skeleton_name)  # skeleton name
			+ FLOAT_SIZE                                 # scale
		)