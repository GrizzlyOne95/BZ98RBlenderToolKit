# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

class BZMapFormat:
	INDEXED = 0
	ARGB4444 = 1
	RGB565 = 2
	ARGB8888 = 3
	XRGB8888 = 4
	COUNT = 5
	
	bpp = [1, 2, 2, 4, 4]



class BZMap:
	
	def __init__(self):
		self.row_byte_size = 0
		self.pixel_format = BZMapFormat.ARGB8888
		self.height = 0
		self._unknown = 0
		self.buffer = None
	
	def set_size(self, width, height):
		self.height = height
		self.row_byte_size = width * BZMapFormat.bpp[self.pixel_format]
	
	def get_size(self):
		return (self.row_byte_size // BZMapFormat.bpp[self.pixel_format], self.height)
	
	def get_pixel_count(self):
		return (self.row_byte_size // BZMapFormat.bpp[self.pixel_format]) * self.height
	
	def get_byte_count(self):
		return self.row_byte_size * self.height
		
	
	def set_buffer(self, buffer):
		mv = memoryview(buffer)
		if(mv.nbytes != self.row_byte_size * self.height):
			raise ValueError(f"Incorrect buffer size! Expected size {self.row_byte_size * self.height}, got {mv.nbytes}")
		self.buffer = mv
	
	def get_buffer(self):
		if(self.buffer is not None):
			return self.buffer.obj
		else:
			return None






