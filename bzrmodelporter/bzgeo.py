import numpy as np
from .spacial import (
	Color3, UV, Vector3,
)

GEO_TAG = int.from_bytes(b".GEO", 'big', signed=True)

class SurfacePlane:
	def __init__(self, surface_normal=None, distance=0.0):
		self.surface_normal = surface_normal or Vector3()
		self.distance = distance or 0.0

class FaceNode:
	def __init__(self, vertex_index=0, vertex_normal_index=0, uv=None):
		self.vertex_index = vertex_index or 0
		self.vertex_normal_index = vertex_normal_index or 0
		self.uv = uv or UV()

class Face:
	def __init__(self, index):
		self.index = index
		self.color = Color3()
		self.plane = SurfacePlane()
		self.poly_area = 0.0
		self.shade_type = 4
		self.texture_type = 1
		self.xluscent_type = 0
		self.texture_name = ""  # len 13
		self.parent_face_index = 0
		self.tree_branch = 0
		self.wireframe = []       # wireframe is a list of face nodes
		
	def create_face_node(self, vertex_index=0, vertex_normal_index=0, uv=None):
		face_node = FaceNode(vertex_index, vertex_normal_index, uv)
		self.wireframe.append(face_node)
		return face_node
	
	def triangles(self):
		degree = len(self.wireframe)
		for i in range(1, degree-1):
			yield (
				self.wireframe[0],
				self.wireframe[i],
				self.wireframe[i+1],
			)

class Geo:
	def __init__(self):
		self._tag = GEO_TAG
		self._checksum = 0
		self.name = ""
		self.vert_count = 0
		self.flags = 0
		self.vertex_pos_buffer = np.empty(0, dtype="<3f")
		self.vertex_normal_buffer = np.empty(0, dtype="<3f")
		self.face_list = []
		self.face_map = {}
	
	def create_face(self, index):
		face = Face(index)
		self.face_list.append(face)
		self.face_map[index] = face
		return face
	
	def faces(self):
		return iter(self.face_list)








