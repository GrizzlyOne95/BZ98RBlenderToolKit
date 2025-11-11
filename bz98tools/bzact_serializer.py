# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

import struct


class BZActSerializer:
	def __init__(self):
		self.endian = 'little'
	
	def deserialize(self, stream):
		f = '<3B' if self.endian == 'little' else '>3B'
		return [
			list(struct.unpack(f, stream.read(3)))
			for i in range(256)
		]
	
	def serialize(self, stream, palatte):
		for i in range(256):
			stream.write(struct.unpack_from(f, palatte[i]))

