# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

import numpy as np

from .spacial import (
    Vector3, Quaternion,
)



class AnimBlend:
	AVERAGE = 0x0000
	CUMULATIVE = 0x0001
	
	name_map = {
		AVERAGE: 'AVERAGE',
		CUMULATIVE: 'CUMULATIVE',
	}
	
	def label(ab, full=False):
		if(ab in AnimBlend.name_map):
			if(full):
				return f"{AnimBlend.name_map[ab]}[0x{ab:04X}]"
			else:
				return AnimBlend.name_map[ab]
		else:
			return f"AnimBlend[0x{ab:04X}]"
	
	def isvalid(ab):
		return ab in AnimBlend.name_map

class LinkedSkeletonAnimationSource:
	def __init__(self):
		self.skeleton_name = None
		self.scale = 1.0

class KeyFrame:
	def __init__(self, time, rot=None, trans=None, scale=None):
		self.time = time
		self.rotation = rot or Quaternion()
		self.translation = trans or Vector3()
		self.scale = scale or Vector3(1.0, 1.0, 1.0)

class AnimationTrack:
	def __init__(self, target_bone):
		self.target_bone = target_bone
		self.keyframe_list = []
	
	def create_keyframe(self, time, rot=None, trans=None, scale=None):
		keyframe = KeyFrame(time, rot, trans, scale)
		self.keyframe_list.append(keyframe)
		return keyframe
	
	def sort(self):
		self.keyframe_list.sort(key=lambda kf: kf.time)
		

class Animation:
	def __init__(self):
		self.name = None
		self.duration = 0.0
		self.use_base_keyframe = False
		self.base_keyframe_animation_name = None
		self.base_keyframe_time = 0.0
		self.track_map = {}
	
	def create_track(self, bone):
		if(bone.handle in self.track_map):
			raise Exception(f"Animation {self.name} already has a track for bone {bone}")
		track = AnimationTrack(bone)
		self.track_map[bone.handle] = track
		return track
	
	def get_track(self, bone_handle):
		return self.track_map[bone_handle]
	
	def tracks(self):
		return self.track_map.values()


class Bone:
	def __init__(self, skeleton, name, handle, pos=None, ori=None, scale=None):
		self.skeleton = skeleton
		self.name = name
		self.handle = handle
		self.parent = None
		self.children = []
		self.position = pos or Vector3()
		self.orientation = ori or Quaternion()
		self.scale = scale or Vector3(1.0, 1.0, 1.0)
	
	def __str__(self):
		return f"{self.name} [{self.handle}]"
	
	def add_child(self, child):
		if(child.parent is not None):
			raise Exception(f"Could not parent bone {child} to bone {self} - Already parented to bone {child.parent}")
		if(child in self.children):
			raise Exception(f"Bone {child} is already a child of bone {self}!")
		self.children.append(child)
		child.parent = self
	
	def remove_child(self, child):
		if(child.parent != self):
			if(child.parent is None):
				raise Exception(f"Cannot remove child bone {child} from {self}; Bone has no parent")
			else:
				raise Exception(f"Cannot remove child bone {child} from {self}; Bone is a child of bone {child.parent}")
		if(child not in self.children):
			raise Exception(f"Cannot remove child bone {child} from {self}; Child is not in children")
		self.children.remove(child)
		child.parent = None
	
	def ancestors(self):
		bone = self.parent
		while(bone is not None):
			yield bone
			bone = bone.parent
	
	def descendants(self):
		for child in self.children:
			yield child
			yield from child.descendants()
	
	def change_name(self, name):
		del self.skeleton.name_map[self.name]
		self.skeleton.name_map[name] = self
		self.name = name


class Skeleton:
	def __init__(self):
		self.animation_map = {}
		self.blendmode = AnimBlend.AVERAGE
		self.bone_map = {} # maps bone handles onto bones
		self.name_map = {} # maps bone names onto bones
		self.linked_skeleton_animation_source_list = []
	
	def create_bone(self, name, handle, pos=None, ori=None, scale=None):
		#if(name in self.name_map):
		#	raise Exception(f"Bone with name '{name}' [{handle} | {self.name_map[name].handle}] already exists!")
		if(handle in self.bone_map):
			raise Exception(f"Bone with handle {handle} ('{name}' | '{self.bone_map[handle].name}') already exists!")
			
		bone = Bone(self, name, handle, pos, ori, scale)
		self.bone_map[handle] = bone
		self.name_map[name] = bone
		return bone
	
	def remove_bone(self, bone, remove_descendants=False):
		if(bone not in self.bone_map.values()):
			raise Exception(f"Bone {bone} is not in skeleton; Cannot remove bone.")
		
		if(remove_descendants):
			# Remove children bones from skeleton
			for child in bone.children:
				self.remove_bone(child, remove_descendants=True)
			
		else:
			# Detach children bones
			for child in bone.children:
				child.parent = None
			
			# Move them to the parent bone if applicable
			if(bone.parent != None):
				for child in bone.children:
					bone.parent.add_child(child)
		
		# Remove bone from parent bone
		if(bone.parent != None):
			bone.parent.remove_child(bone)
		
		# Remove bone from skeleton
		del self.bone_map[bone.handle]
		del self.name_map[bone.name]
	
	def get_bone(self, handle):
		return self.bone_map[handle]
	
	def get_bone_by_name(self, name):
		return self.name_map[name]
	
	def bone_name_exists(self, name):
		return name in self.name_map
		
	def parent_bone(self, child, parent):
		if(child.parent is not None):
			child.parent.children.remove(child)
			child.parent = None
		if(parent is not None):
			child.parent = parent
			parent.children.append(child)
	
	def root_bones(self):
		return iter(bone for bone in self.bone_map.values() if bone is not None and bone.parent is None)
	
	def bones(self):
		return sorted(self.bone_map.values(), key=lambda bone: bone.handle)
		
	def create_animation(self, name, duration):
		if(name in self.animation_map):
			raise Exception(f"Animation {name} already exists!")
		animation = Animation()
		animation.name = name
		animation.duration = duration
		self.animation_map[name] = animation
		return animation
	
	def animations(self):
		return self.animation_map.values()
	
	def create_linked_skeleton_animation_source(self, skeleton_name, scale):
		lsas = None
		for lsas2 in skeleton.linked_skeleton_animation_source_list:
			if(skeleton_name == lsas2.skeleton_name):
				break
		else:
			lsas = LinkedSkeletonAnimationSource()
			lsas.skeleton_name = skeleton_name
			lsas.scale = scale
			skeleton.linked_skeleton_animation_source_list.append(lsas)
		return lsas
	
	def sources(self):
		return iter(self.linked_skeleton_animation_source_list)
	
	def verify(self):
		if(not AnimBlend.isvalid(self.blendmode)):
			return (False, f"Animation blend mode is invalid: {AnimBlend.label(self.blendmode, full=True)}")
		
		for (handle, bone) in self.bone_map.items():
			if(bone is None):
				return (False, f"Bone map is not contiguous; Bone with handle {handle} is None")
			if(handle != bone.handle):
				return (False, f"Bone map is not consistent; Got bone {bone} from handle {handle}")
			if(bone.skeleton != self):
				return (False, f"Bone {bone} is in a different skeleton {bone.skeleton}")
			if(bone.name not in self.name_map):
				return (False, f"Bone {bone} name is not in name map")
			if(self.name_map[bone.name] != bone):
				return (False, f"Name map is not consistent; Got bone {self.name_map[bone.name]} from name {bone.name}")
			if(bone.parent is not None):
				if(bone.parent not in self.bone_map.values()):
					return (False, f"Parent bone {bone.parent} of {bone} is not in bone list")
				if(bone not in bone.parent.children):
					return (False, f"Bone {bone} is not a child of its parent bone {bone.parent}")
				parent_list = []
				b = bone
				while(True):
					if(b in parent_list):
						parent_list.append(b)
						return (False, f"Cyclic bone hierarchy: {parent_list}")
					if(b.parent is None):
						break
					parent_list.append(b)
					b = b.parent
			
			bone_set = set()
			for child in bone.children:
				if(child not in self.bone_map.values()):
					return (False, f"Child bone {child} of bone {bone} is not in bone list")
				if(child in bone_set):
					return (False, f"Bone {bone} multiply contains child bone {child}")
				if(child.parent != bone):
					return (False, f"Bone {bone} is not the parent of its child bone {child}")
				bone_set.add(child)
		
		for (name, bone) in self.name_map.items():
			if(bone not in self.bone_map.values()):
				return (False, f"Name-mapped bone {bone} not in bone map")
			if(bone.name != name):
				return (False, f"Name map inconsistent; Got bone {bone} from name '{name}'")
		
		# TODO: Verify animations and linked animation sources
		return (True, "Verification successful")
