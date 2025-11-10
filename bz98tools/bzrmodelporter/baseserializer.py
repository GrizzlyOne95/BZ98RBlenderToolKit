# Text encoding/decoding currently uses 'latin-1' (iso-8859-1) encoding.
#   I'm not sure this is the most appropriate solution.


import struct

from .spacial import (
	Color3, UV,
	Vector3, Quaternion, Transform,
)

BOOL_SIZE = 1
UBYTE_SIZE = 1
SBYTE_SIZE = 1
USHORT_SIZE = 2
SSHORT_SIZE = 2
UINT_SIZE = 4
SINT_SIZE = 4
FLOAT_SIZE = 4
DOUBLE_SIZE = 8

COLOR_SIZE = 3*UBYTE_SIZE            # 3
UV_SIZE = 2*FLOAT_SIZE          # 8
VECTOR3_SIZE = 3*FLOAT_SIZE     # 12
QUATERNION_SIZE = 4*FLOAT_SIZE  # 16
TRANSFORM_SIZE = 4*VECTOR3_SIZE # 48

class AbruptEOFError(EOFError):
	pass

class BaseSerializer:
	def __init__(self, stream, endian='little'):
		self.stream = stream
		
		self.endian = None
		self.endiansymbol = None
		
		self.set_endian(endian)
	
	def set_endian(self, endian):
		if(endian == 'little'):
			self.endian = 'little'
			self.endiansymbol = '<'
		elif(endian == 'big'):
			self.endian = 'big'
			self.endiansymbol = '>'
		else:
			raise ValueError(f"{endian} is not a valid endianness")
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Read Methods
	
	def read_raw(self, bytecount):
		b = self.stream.read(bytecount)
		if(len(b) < bytecount):
			raise EOFError() if len(b) == 0 else AbruptEOFError()
		return b
	
	def read_bool(self):
		b = self.read_raw(BOOL_SIZE)
		return b != b"\x00"
	
	def read_ubyte(self):
		b = self.read_raw(UBYTE_SIZE)
		return int.from_bytes(b, self.endian)
		
	def read_sbyte(self):
		b = self.read_raw(SBYTE_SIZE)
		return int.from_bytes(b, self.endian, signed=True)
	
	def read_ushort(self):
		b = self.read_raw(USHORT_SIZE)
		return int.from_bytes(b, self.endian)
		
	def read_sshort(self):
		b = self.read_raw(SSHORT_SIZE)
		return int.from_bytes(b, self.endian, signed=True)
		
	def read_uint(self):
		b = self.read_raw(UINT_SIZE)
		return int.from_bytes(b, self.endian)
	
	def read_uint_array(self, length):
		b = self.read_raw(UINT_SIZE*length)
		return struct.unpack(self.endiansymbol+str(length)+"I", b)
		
	def read_sint(self):
		b = self.read_raw(SINT_SIZE)
		return int.from_bytes(b, self.endian, signed=True)
	
	def read_sint_array(self, length):
		b = self.read_raw(UINT_SIZE*length)
		return struct.unpack(self.endiansymbol+str(length)+"i", b)
	
	def read_float(self):
		b = self.read_raw(FLOAT_SIZE)
		return struct.unpack(self.endiansymbol+"f", b)[0]
	
	def read_float_array(self, length):
		b = self.read_raw(FLOAT_SIZE*length)
		return struct.unpack(self.endiansymbol+str(length)+"f", b)
	
	def read_string_nlt(self):
		'''Read newline-terminated string'''
		b = self.stream.readline()
		if(len(b) < 1):
			raise AbruptEOFError()
		if(b[-1] == 0x0A):
			b = b[:-1]
		return b.decode('latin-1')
		
	def read_string_fl_nt(self, length):
		'''Read fixed-length null-terminated string'''
		b = self.read_raw(length)
		b = b.partition(b"\0")[0]
		return b.decode('latin-1')
		
	def read_uv_rd(self):
		b = self.read_raw(UV_SIZE)
		return UV(*struct.unpack(self.endiansymbol+"2f", b))
	
	def read_color_rgb888(self):
		b = self.read_raw(COLOR_SIZE)
		return Color3(*struct.unpack("3B", b))
	
	def read_vector3_ruf(self):
		b = self.read_raw(VECTOR3_SIZE)
		return Vector3.from_array_ruf(struct.unpack(self.endiansymbol+"3f", b))
	
	def read_vector3_luf(self):
		b = self.read_raw(VECTOR3_SIZE)
		return Vector3.from_array_luf(struct.unpack(self.endiansymbol+"3f", b))
	
	def read_quaternion_sruf_right(self):
		b = self.read_raw(QUATERNION_SIZE)
		return Quaternion.from_array_sruf_right(struct.unpack(self.endiansymbol+"4f", b))
	
	def read_quaternion_lufs_left(self):
		b = self.read_raw(QUATERNION_SIZE)
		return Quaternion.from_array_lufs_left(struct.unpack(self.endiansymbol+"4f", b))
	
	def read_transform_rufp(self):
		b = self.read_raw(TRANSFORM_SIZE)
		return Transform.from_array_rufp_xyz(struct.unpack(self.endiansymbol+"12f", b))
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Write Methods
	def write_raw(self, val):
		self.stream.write(val)
	
	def write_bool(self, val):
		self.stream.write(b"\x01" if val else b"\x00")
		
	def write_ubyte(self, val):
		self.stream.write(val.to_bytes(UBYTE_SIZE, self.endian))
		
	def write_sbyte(self, val):
		self.stream.write(val.to_bytes(SBYTE_SIZE, self.endian, signed=True))
	
	def write_ushort(self, val):
		self.stream.write(val.to_bytes(USHORT_SIZE, self.endian))
		
	def write_sshort(self, val):
		self.stream.write(val.to_bytes(SSHORT_SIZE, self.endian, signed=True))
		
	def write_uint(self, val):
		self.stream.write(val.to_bytes(UINT_SIZE, self.endian))
	
	def write_uint_array(self, vals, length):
		self.stream.write(struct.pack(self.endiansymbol+str( min(length, len(vals)) )+"I", *vals))
		
	def write_sint(self, val):
		self.stream.write(val.to_bytes(SINT_SIZE, self.endian, signed=True))
	
	def write_sint_array(self, vals, length):
		self.stream.write(struct.pack(self.endiansymbol+str( min(length, len(vals)) )+"i", *vals))
	
	def write_float(self, val):
		self.stream.write(struct.pack(self.endiansymbol+"f", val))
	
	def write_float_array(self, vals, length):
		self.stream.write(struct.pack(self.endiansymbol+str( min(length, len(vals)) )+"f", *vals))
		
	def write_string_nlt(self, s): # TODO: Experiment with string parsing behavior
		'''Write newline-terminated string'''
		self.stream.write((s + "\n").encode('latin-1'))
		
	def write_string_fl_nt(self, s, length):
		'''Write fixed-length null-terminated string'''
		self.stream.write((s.ljust(length, "\0")).encode('latin-1'))
	
	def write_uv_rd(self, val):
		self.stream.write(struct.pack(self.endiansymbol+"2f", val.u, val.v))
	
	def write_color_rgb888(self, val):
		self.stream.write(struct.pack("3B", val.r, val.g, val.b))
	
	def write_vector3_ruf(self, val):
		self.stream.write(struct.pack(self.endiansymbol+"3f", *val.to_ruf()))
	
	def write_vector3_luf(self, val):
		self.stream.write(struct.pack(self.endiansymbol+"3f", *val.to_luf()))
	
	def write_quaternion_sruf_right(self, val):
		self.stream.write(struct.pack(self.endiansymbol+"4f", *val.to_sruf_right()))
	
	def write_quaternion_lufs_left(self, val):
		self.stream.write(struct.pack(self.endiansymbol+"4f", *val.to_lufs_left()))
	
	def write_transform_rufp(self, val):
		self.stream.write(struct.pack(self.endiansymbol+"12f", *val.to_rufp_xyz()))
	
	#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	#-# Calc Methods
	
	def calc_string_nlt_size(self, val):
		return len(val) + 1

