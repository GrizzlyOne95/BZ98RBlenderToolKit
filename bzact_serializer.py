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

