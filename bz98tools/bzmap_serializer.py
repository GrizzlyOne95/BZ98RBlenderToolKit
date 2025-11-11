# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

from .bzmap import BZMap


class BZMapSerializer:
	def __init__(self):
		self.endian = 'little'
	
	def deserialize(self, stream, bzmap):
		bzmap.row_byte_size = self.read_ushort(stream)
		bzmap.pixel_format = self.read_ushort(stream)
		bzmap.height = self.read_ushort(stream)
		bzmap._unknown = self.read_ushort(stream)
		bzmap.set_buffer(stream.read(bzmap.get_byte_count()))
	
	def read_ushort(self, stream):
		b = stream.read(2)
		if(len(b) < 2):
			raise EOFError()
		return int.from_bytes(b, self.endian)
	
	
	def serialize(self, stream, bzmap):
		self.write_ushort(bzmap.row_byte_size)
		self.write_ushort(bzmap.pixel_format)
		self.write_ushort(bzmap.height)
		self.write_ushort(bzmap._unknown)
		stream.write(bzmap.buffer[:bzmap.get_byte_count()])
	
	
	def write_ushort(self, stream, val):
		stream.write(val.to_bytes(2, self.endian))

