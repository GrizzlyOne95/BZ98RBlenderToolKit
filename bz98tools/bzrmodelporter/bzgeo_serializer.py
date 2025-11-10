from .bzgeo import (
	Geo,
	GEO_TAG,
)
from .bz_baseserializer import (
	BZBaseSerializer,
)

class GeoSerializer(BZBaseSerializer):
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Read Methods
	
	def read(self, geo=None, ignore_header_tag=False):
		if(geo is None):
			geo = Geo()
		
		self.read_header(geo, ignore_header_tag)
		geo.name = self.read_string(16)
		geo.vert_count = self.read_sint()
		poly_count = self.read_sint()
		geo.flags = self.read_sint()
		
		geo.vertex_pos_buffer = self.read_npvector3_array(geo.vert_count)
		geo.vertex_normal_buffer = self.read_npvector3_array(geo.vert_count)
		
		self.read_face_list(geo, poly_count)
		
		return geo
	
	def read_header(self, geo, ignore_header_tag):
		tag = self.read_sint()
		if(not ignore_header_tag and tag != GEO_TAG):
			raise Exception(f"4-byte header tag does not match expected value 0x{GEO_TAG:X}, got 0x{tag:X}")
		
		geo._tag = tag
		geo._checksum = self.read_sint()
	
	def read_face_list(self, geo, poly_count):
		for i in range(poly_count):
			index = self.read_sint()
			vertex_count = self.read_sint()
			face = geo.create_face(index)
			face.color = self.read_color()
			self.read_surface_plane(face.plane)
			face.poly_area = self.read_float()
			face.shade_type = self.read_ubyte()
			face.texture_type = self.read_ubyte()
			face.xluscent_type = self.read_ubyte()
			face.texture_name = self.read_string(13)
			face.parent_face_index = self.read_sint()
			face.tree_branch = self.read_uint()
			self.read_wireframe(face, vertex_count)  # List of FaceNode objects
			
	def read_surface_plane(self, plane):
		plane.surface_normal = self.read_vector3()
		plane.distance = self.read_float()
	
	def read_wireframe(self, face, vertex_count):
		for i in range(vertex_count):
			face_node = face.create_face_node(
				vertex_index=self.read_sint(),
				vertex_normal_index=self.read_sint(),
				uv=self.read_uv(),
			)
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Write Methods
	
	def write(self, geo):
		self.write_header(geo)
		
		self.write_string(geo.name, 16)
		self.write_sint(geo.vert_count)
		self.write_sint(len(geo.face_list))
		self.write_sint(geo.flags)
		
		self.write_npvector3_array(geo.vertex_pos_buffer)
		self.write_npvector3_array(geo.vertex_normal_buffer)
		
		self.write_face_list(geo.face_list)
	
	def write_header(self, geo):
		self.write_sint(geo._tag)
		self.write_sint(geo._checksum)
	
	def write_face_list(self, face_list):
		for face in face_list:
			self.write_sint(face.index)
			self.write_sint(len(face.wireframe))
			self.write_color(face.color)
			self.write_surface_plane(face.plane)
			self.write_float(face.poly_area)
			self.write_ubyte(face.shade_type)
			self.write_ubyte(face.texture_type)
			self.write_ubyte(face.xluscent_type)
			self.write_string(face.texture_name, 13)
			self.write_sint(face.parent_face_index)
			self.write_sint(face.tree_branch)
			self.write_wireframe(face.wireframe)  # List of FaceNode objects
			
	def write_surface_plane(self, plane):
		self.write_vector3(plane.surface_normal)
		self.write_float(plane.distance)
	
	def write_wireframe(self, wireframe):
		for face_node in wireframe:
			self.write_sint(face_node.vertex_index)
			self.write_sint(face_node.vertex_normal_index)
			self.write_uv(face_node.uv)
