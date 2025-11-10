import numpy as np
import struct

from .spacial import (
	Color3, UV,
	Vector3, Quaternion, Transform,
)

from .baseserializer import (
	BaseSerializer,
	FLOAT_SIZE,
)


COLOR_SIZE = 3
UV_SIZE = 2*FLOAT_SIZE          # 8
VECTOR3_SIZE = 3*FLOAT_SIZE     # 12
QUATERNION_SIZE = 4*FLOAT_SIZE  # 16
TRANSFORM_SIZE = 4*VECTOR3_SIZE # 48

class BZBaseSerializer(BaseSerializer):
	def read_npvector3_array(self, count):
		return np.frombuffer(self.read_raw(count * VECTOR3_SIZE), dtype="<3f", count=count)
		
	def write_npvector3_array(self, vals):
		self.stream.write(vals.tobytes())
	
	read_string = BaseSerializer.read_string_fl_nt
	write_string = BaseSerializer.write_string_fl_nt
	read_uv = BaseSerializer.read_uv_rd
	write_uv = BaseSerializer.write_uv_rd
	read_color = BaseSerializer.read_color_rgb888
	write_color = BaseSerializer.write_color_rgb888
	read_vector3 = BaseSerializer.read_vector3_ruf
	write_vector3 = BaseSerializer.write_vector3_ruf
	read_quaternion = BaseSerializer.read_quaternion_sruf_right
	write_quaternion = BaseSerializer.write_quaternion_sruf_right
	read_transform = BaseSerializer.read_transform_rufp
	write_transform = BaseSerializer.write_transform_rufp
