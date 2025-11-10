import numpy as np
import math
from .utils import clip

class Color3:
	def __init__(self, r=0, g=0, b=0):
		self.r = r
		self.g = g
		self.b = b
	
	@staticmethod
	def from_color3(color_rgb):
		return Color3(color_rgb.r, color_rgb.g, color_rgb.b)
	
	@staticmethod
	def from_array_rgb(ar):
		return Color3(ar[0], ar[1], ar[2])
	
	def __eq__(self, other):
		return self.r == other.r and self.g == other.g and self.b == other.b
	
	def __repr__(self):
		return f"Color3(r:0x{self.r:02X}, g:0x{self.g:02X}, b:0x{self.b:02X})"
	
	def __str__(self):
		return f"[{self.r:02X}, {self.g:02X}, {self.b:02X}]"

class UV:
	def __init__(self, u=0.0, v=0.0):
		self.u = u
		self.v = v
	
	@staticmethod
	def from_uv(uv):
		return UV(uv.u, uv.v)
	
	@staticmethod
	def from_array(ar):
		return UV(ar[0], ar[1])
	
	def __eq__(self, other):
		return self.u == other.u and self.v == other.v
	
	def __repr__(self):
		return f"UV({self.u}, {self.v})"
	
	def __str__(self):
		return f"[{self.u}, {self.v}]"

class Vector3:
	def __init__(self, x=0.0, y=0.0, z=0.0):
		self.x = x   # Right
		self.y = y   # Up
		self.z = z   # Front
	
	@staticmethod
	def from_vector3(vec):
		return Vector3(vec.x, vec.y, vec.z)
	
	@staticmethod
	def from_ruf(r, u, f):
		return Vector3(r, u, f)
	
	@staticmethod
	def from_luf(l, u, f):
		return Vector3(-l, u, f)
	
	@staticmethod
	def from_array_ruf(ar):
		return Vector3(ar[0], ar[1], ar[2])
	
	@staticmethod
	def from_array_luf(ar):
		return Vector3(-ar[0], ar[1], ar[2])
	
	def to_ruf(self):
		return (self.x, self.y, self.z)
	
	def to_luf(self):
		return (-self.x, self.y, self.z)
	
	def to_nparray_ruf(self):
		return np.array([self.x, self.y, self.z])
	
	def to_nparray_vector_ruf(self):
		return np.array([[self.x], [self.y], [self.z]])
	
	def __neg__(self):
		return Vector3(
			-self.x,
			-self.y,
			-self.z,
		)
	
	def __add__(self, other):
		return Vector3(
			self.x + other.x,
			self.y + other.y,
			self.z + other.z,
		)
	
	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		self.z += other.z
		return self
	
	def __sub__(self, other):
		return Vector3(
			self.x - other.x,
			self.y - other.y,
			self.z - other.z,
		)
	
	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		self.z -= other.z
		return self
	
	def __mul__(self, other):
		return Vector3(
			self.x*other,
			self.y*other,
			self.z*other,
		)
	
	def __rmul__(self, other):
		return self*other
	
	def __imul__(self, other):
		self.x *= other
		self.y *= other
		self.z *= other
		return self
	
	def __truediv__(self, other):
		return Vector3(
			self.x/other,
			self.y/other,
			self.z/other,
		)
	
	def __itruediv__(self, other):
		self.x /= other
		self.y /= other
		self.z /= other
		return self
	
	def squag(self):
		return math.sqrt(self.x*selfx + self.y*self.y + self.z*self.z)
	
	def mag(self):
		return math.sqrt(self.x*selfx + self.y*self.y + self.z*self.z)
	
	def set(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
		return self
	
	def set_vector3(self, v):
		self.x = v.x
		self.y = v.y
		self.z = v.z
		return self
	
	def copy(self):
		return Vector3(self.x, self.y, self.z)
	
	def dot(self, other):
		return self.x*other.x + self.y*other.y + self.z*other.z
	
	def cross(self, other):
		return Vector3(
			self.y*other.z - self.z*other.y,
			self.z*other.x - self.x*other.z,
			self.x*other.y - self.y*other.x,
		)
	
	@staticmethod
	def triangle_cross(v0, v1, v2):
		x0 = v1.x - v0.x
		y0 = v1.y - v0.y
		z0 = v1.z - v0.z
		x1 = v2.x - v0.x
		y1 = v2.y - v0.y
		z1 = v2.z - v0.z
		return Vector3(
			y0*z1 - z0*y1,
			z0*x1 - x0*z1,
			x0*y1 - y0*x1,
		)
	
	@staticmethod
	def lerp(v0, v1, n):
		'''Linear interpolation between vectors v0 and v1 such that the
		range n=[0, 1] maps to the range lerp(v0, v1, n)=[v0, v1]
		'''
		return v0 + n*(v1 - v0)
	
	def rotate(self, q):
		'''Rotate self by quaternion q
		
		Rotation is right-handed, and assumes q is a unit quaternion.
		'''
		x = (
			self.x * (q.w*q.w + q.x*q.x - q.y*q.y - q.z*q.z)
			+ self.y * (q.y*q.x + q.w*q.z)*2
			+ self.z * (q.z*q.x - q.w*q.y)*2
		)
		y = (
			self.x * (q.x*q.y - q.w*q.z)*2
			+ self.y * (q.w*q.w + q.y*q.y - q.z*q.z - q.x*q.x)
			+ self.z * (q.z*q.y + q.w*q.x)*2
		)
		z = (
			self.x * (q.x*q.z + q.w*q.y)*2
			+ self.y * (q.y*q.z - q.w*q.x)*2
			+ self.z * (q.w*q.w + q.z*q.z - q.x*q.x - q.y*q.y)
		)
		
		self.x = x
		self.y = y
		self.z = z
		return self
	
	def translate(self, v):
		'''Translate self by vector v'''
		self.x += v.x
		self.y += v.y
		self.z += v.z
		return self
	
	def antitranslate(self, v):
		'''Translate self by inverse vector -v'''
		self.x -= v.x
		self.y -= v.y
		self.z -= v.z
		return self
	
	def transform(self, t):
		'''Transform self by matrix t'''
		x = self.x * t.rx + self.y * t.ux + self.z * t.fx + t.px
		y = self.x * t.ry + self.y * t.uy + self.z * t.fy + t.py
		z = self.x * t.rz + self.y * t.uz + self.z * t.fz + t.pz
		self.x = x
		self.y = y
		self.z = z
		return self
	
	def normalize(self):
		'''Scale self to be of unit length'''
		mag = math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
		if(mag > 0):
			self.x /= mag
			self.y /= mag
			self.z /= mag
			return self
		self.x = 1.0
		self.y = 0.0
		self.z = 0.0
		return self
	
	def isNaN(self):
		return self.x != self.x or self.y != self.y or self.z != self.z
	
	def __eq__(self, other):
		return self.x == other.x and self.y == other.y and self.z == other.z
	
	def __repr__(self):
		return f"Vector3(x={self.x}, y={self.y}, z={self.z})"
	
	def __str__(self):
		return f"[{self.x}, {self.y}, {self.z}]"


class Quaternion:
	def __init__(self, w=1.0, x=0.0, y=0.0, z=0.0):
		self.w = w   # Scalar
		self.x = x   # Right   | x*y == z
		self.y = y   # Up      | right-handed rotation
		self.z = z   # Front
	
	@staticmethod
	def from_quaternion(quat):
		return Quaternion(quat.w, quat.x, quat.y, quat.z)
	
	@staticmethod
	def from_sruf_right(s, r, u, f):
		return Quaternion(s, r, u, f)
	
	@staticmethod
	def from_lufs_left(l, u, f, s):
		return Quaternion(s, -l, u, f)
	
	@staticmethod
	def from_array_sruf_right(ar):
		return Quaternion(ar[0], ar[1], ar[2], ar[3])
	
	@staticmethod
	def from_array_lufs_left(ar):
		return Quaternion(ar[3], -ar[0], ar[1], ar[2])
	
	@staticmethod
	def slerp(a, b, n):
		# a.rotate(delta) = b
		delta = b.copy().antiprerotate(a)
		
		# `delta.w` is like the adjacent, while `sqrt(delta.x^2, delta.y^2, delta.z^2)` is the opposite.
		# The hypotenuse in this analogy should be unit length.
		# The angle of this triangle is half the angle by which `delta` rotates space!
		#          (half the angle difference between `a` and `b`)
		mag3d = math.sqrt(delta.x**2 + delta.y**2 + delta.z**2)
		if(mag3d == 0):
			return a
		theta = math.acos(clip(-1.0, delta.w, 1.0))
		c = math.cos(n * theta)
		s = math.sin(n * theta)
		return a.copy().rotate(Quaternion(
			c,
			delta.x/mag3d * s,
			delta.y/mag3d * s,
			delta.z/mag3d * s,
		))
	
	def to_sruf_right(self):
		return (self.w, self.x, self.y, self.z)
	
	def to_lufs_left(self):
		return (-self.x, self.y, self.z, self.w)
	
	def set(self, w, x, y, z):
		'''Set the w, x, y, and z components of this quaternion'''
		self.w = w
		self.x = x
		self.y = y
		self.z = z
		return self
	
	def set_quaternion(self, q):
		'''Set the components of this quaternion equal to another'''
		self.w = q.w
		self.x = q.x
		self.y = q.y
		self.z = q.z
		return self
	
	def rotate(self, other):
		'''Rotate self by other'''
		# Right multiply
		w = self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z
		x = self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y
		y = self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x
		z = self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w
		self.w = w
		self.x = x
		self.y = y
		self.z = z
		return self
	
	def prerotate(self, q):
		'''Prerotate self by q'''
		# Left multiply
		w = self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z
		x = self.w*other.x + self.x*other.w - self.y*other.z + self.z*other.y
		y = self.w*other.y + self.x*other.z + self.y*other.w - self.z*other.x
		z = self.w*other.z - self.x*other.y + self.y*other.x + self.z*other.w
		self.w = w
		self.x = x
		self.y = y
		self.z = z
		return self
	
	def antirotate(self, other):
		'''Rotate self by q inverse'''
		# Right divide
		squag = other.squag()
		w = ( + self.w*other.w + self.x*other.x + self.y*other.y + self.z*other.z) / squag
		x = ( - self.w*other.x + self.x*other.w - self.y*other.z + self.z*other.y) / squag
		y = ( - self.w*other.y + self.x*other.z + self.y*other.w - self.z*other.x) / squag
		z = ( - self.w*other.z - self.x*other.y + self.y*other.x + self.z*other.w) / squag
		self.w = w
		self.x = x
		self.y = y
		self.z = z
		return self
	
	def antiprerotate(self, other):
		'''Prerotate self by q inverse'''
		# Left divide
		squag = other.squag()
		w = ( + self.w*other.w + self.x*other.x + self.y*other.y + self.z*other.z) / squag
		x = ( - self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y) / squag
		y = ( - self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x) / squag
		z = ( - self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w) / squag
		self.w = w
		self.x = x
		self.y = y
		self.z = z
		return self
	
	def squag(self):
		'''Squared magnitude'''
		return self.w*self.w + self.x*self.x + self.y*self.y + self.z*self.z
	
	def mag(self):
		'''Magnitude'''
		return math.sqrt(self.w*self.w + self.x*self.x + self.y*self.y + self.z*self.z)
	
	def normalize(self):
		'''Normalize to unit quaternion in place'''
		mag = math.sqrt(self.w*self.w + self.x*self.x + self.y*self.y + self.z*self.z)
		if(mag <= 0):
			self.w = 1.0
			self.x = 0.0
			self.y = 0.0
			self.z = 0.0
			return self
		self.w /= mag
		self.x /= mag
		self.y /= mag
		self.z /= mag
		return self
	
	def reciprocate(self):
		'''Reciprocate self in place and return'''
		squag = self.squag()
		self.w /= squag
		self.x /= -squag
		self.y /= -squag
		self.z /= -squag
		return self
	
	def conjugate(self):
		self.x *= -1
		self.y *= -1
		self.z *= -1
		return self
	
	def to_transform(self):
		w = self.w
		x = self.x
		y = self.y
		z = self.z
		return Transform(
			w*w + x*x - y*y - z*z,
			2*(x*y - w*z),
			2*(x*z + w*y),
			
			2*(x*y + w*z),
			w*w - x*x + y*y - z*z,
			2*(y*z - w*x),
			
			2*(x*z - w*y),
			2*(y*z + w*x),
			w*w - x*x - y*y + z*z,
		)
	
	def copy(self):
		return Quaternion(self.w, self.x, self.y, self.z)
	
	def __eq__(self, other):
		return self.w == other.w and self.x == other.x and self.y == other.y and self.z == other.z
	
	def __repr__(self):
		return f"Quaternion(w:{self.w}, x:{self.x}, y:{self.y}, z:{self.z})"
	
	def __str__(self):
		return f"[{self.w}, {self.x}, {self.y}, {self.z}]"

class Transform:
	def __init__(self, rx=1.0, ry=0.0, rz=0.0, ux=0.0, uy=1.0, uz=0.0, fx=0.0, fy=0.0, fz=1.0, px=0.0, py=0.0, pz=0.0):
		#                Vector  Component
		self.rx = rx  # Right,   Right
		self.ry = ry  # Right,   Up
		self.rz = rz  # Right,   Front
		self.ux = ux  # Up,      Right
		self.uy = uy  # Up,      Up
		self.uz = uz  # Up,      Front
		self.fx = fx  # Front,   Right
		self.fy = fy  # Front,   Up
		self.fz = fz  # Front,   Front
		self.px = px  # Posit,   Right
		self.py = py  # Posit,   Up
		self.pz = pz  # Posit,   Front
	
	def __matmul__(self, other):
		return Transform(
			rx=self.rx*other.rx + self.ux*other.ry + self.fx*other.rz,
			ry=self.ry*other.rx + self.uy*other.ry + self.fy*other.rz,
			rz=self.rz*other.rx + self.uz*other.ry + self.fz*other.rz,
			
			ux=self.rx*other.ux + self.ux*other.uy + self.fx*other.uz,
			uy=self.ry*other.ux + self.uy*other.uy + self.fy*other.uz,
			uz=self.rz*other.ux + self.uz*other.uy + self.fz*other.uz,
			
			fx=self.rx*other.fx + self.ux*other.fy + self.fx*other.fz,
			fy=self.ry*other.fx + self.uy*other.fy + self.fy*other.fz,
			fz=self.rz*other.fx + self.uz*other.fy + self.fz*other.fz,
			
			px=self.rx*other.px + self.ux*other.py + self.fx*other.pz + self.px,
			py=self.ry*other.px + self.uy*other.py + self.fy*other.pz + self.py,
			pz=self.rz*other.px + self.uz*other.py + self.fz*other.pz + self.pz,
		)
	
	@staticmethod
	def from_transform(t):
		return Transform(
			t.rx, t.ry, t.rz,
			t.ux, t.uy, t.uz,
			t.fx, t.fy, t.fz,
			t.px, t.py, t.pz,
		)
	
	@staticmethod
	def from_rufp_xyz(rx, ry, rz, ux, uy, uz, fx, fy, fz, px, py, pz):
		return Transform(
			rx, ry, rz,
			ux, uy, uz,
			fx, fy, fz,
			px, py, pz,
		)
	
	@staticmethod
	def from_array_rufp_xyz(ar):
		return Transform(
			ar[0], ar[1], ar[2],
			ar[3], ar[4], ar[5],
			ar[6], ar[7], ar[8],
			ar[9], ar[10], ar[11],
		)
	
	@staticmethod
	def from_array2d_xyz_rufp(ar):
		return Transform(
			ar[0][0], ar[1][0], ar[2][0],
			ar[0][1], ar[1][1], ar[2][1],
			ar[0][2], ar[1][2], ar[2][2],
			ar[0][3], ar[1][3], ar[2][3],
		)
	
	@staticmethod
	def from_quaternion_translation(q, t):
		w = q.w
		x = q.x
		y = q.y
		z = q.z
		return Transform(
			w*w + x*x - y*y - z*z,
			2*(x*y - w*z),
			2*(x*z + w*y),
			
			2*(x*y + w*z),
			w*w - x*x + y*y - z*z,
			2*(y*z - w*x),
			
			2*(x*z - w*y),
			2*(y*z + w*x),
			w*w - x*x - y*y + z*z,
			
			t.x,
			t.y,
			t.z,
		)
	
	@staticmethod
	def inv_from_quaternion_translation(q, t):
		squag = q.squag()
		w =  q.w / squag
		x = -q.x / squag
		y = -q.y / squag
		z = -q.z / squag
		return Transform(
			w*w + x*x - y*y - z*z,
			2*(x*y - w*z),
			2*(x*z + w*y),
			
			2*(x*y + w*z),
			w*w - x*x + y*y - z*z,
			2*(y*z - w*x),
			
			2*(x*z - w*y),
			2*(y*z + w*x),
			w*w - x*x - y*y + z*z,
			
			(-t.x)*(w*w + x*x - y*y - z*z) + (-t.y)*(2*(x*y + w*z)) + (-t.z)*(2*(x*z - w*y)),
			(-t.x)*(2*(x*y - w*z)) + (-t.y)*(w*w - x*x + y*y - z*z) + (-t.z)*(2*(y*z + w*x)),
			(-t.x)*(2*(x*z + w*y)) + (-t.y)*(2*(y*z - w*x)) + (-t.z)*(w*w - x*x - y*y + z*z),
		)
	
	def to_rufp_xyz(self):
		return (
			self.rx, self.ry, self.rz,
			self.ux, self.uy, self.uz,
			self.fx, self.fy, self.fz,
			self.px, self.py, self.pz,
		)
	
	def posit(self):
		return Vector3(
			self.px,
			self.py,
			self.pz,
		)
	
	def to_nparray_xyz_ruf(self):
		return np.array([
			[self.rx, self.ux, self.fx],
			[self.ry, self.uy, self.fy],
			[self.rz, self.uz, self.fz],
		])
	
	def to_nparray_xyz_rufp(self):
		return np.array([
			[self.rx, self.ux, self.fx, self.px],
			[self.ry, self.uy, self.fy, self.py],
			[self.rz, self.uz, self.fz, self.pz],
		])
	
	def to_nparray_xyzw_rufp(self):
		return np.array([
			[self.rx, self.ux, self.fx, self.px],
			[self.ry, self.uy, self.fy, self.py],
			[self.rz, self.uz, self.fz, self.pz],
			[0.0,      0.0,      0.0,      1.0     ],
		])
	
	
	def compute_orientation(self): 
		'''Return a quaternion describing the same rotation as this transform'''
		if(self.rx + self.uy + self.fz > 0):
			s = math.sqrt(1 + self.rx + self.uy + self.fz) * 2   # s = 4|qw|
			return Quaternion(
				s / 4,                      # |qw|
				(self.fy - self.uz) / s,  # 4*qw*qx/(4|qw|) = sig(qw)*qx
				(self.rz - self.fx) / s,  # 4*qw*qy/(4|qw|) = sig(qw)*qy
				(self.ux - self.ry) / s,  # 4*qw*qz/(4|qw|) = sig(qw)*qz
			)
		elif(self.rx > self.uy and self.rx > self.fz):
			s = math.sqrt(1 + self.rx - self.uy - self.fz) * 2   # s = 4|qx|
			return Quaternion(
				(self.fy - self.uz) / s,  # 4*qw*qx/(4|qx|) = sig(qx)*qw
				s / 4,                      # |qx|
				(self.ux + self.ry) / s,  # 4*qx*qy/(4|qx|) = sig(qx)*qy
				(self.rz + self.fx) / s,  # 4*qz*qx/(4|qx|) = sig(qx)*qz
			)
		elif(self.uy > self.fz):
			s = math.sqrt(1 - self.rx + self.uy - self.fz) * 2   # s = 4|qy|
			return Quaternion(
				(self.rz - self.fx) / s,  # 4*qw*qy/(4|qy|) = sig(qy)*qw
				(self.ux + self.ry) / s,  # 4*qx*qy/(4|qy|) = sig(qy)*qx
				s / 4,                      # |qy|
				(self.fy + self.uz) / s,  # 4*qy*qz/(4|qy|) = sig(qy)*qz
			)
		else:
			s = math.sqrt(1 - self.rx - self.uy + self.fz) * 2   # s = 4|qz|
			return Quaternion(
				(self.ux - self.ry) / s,  # 4*qw*qz/(4|qz|) = sig(qz)*qw
				(self.rz + self.fx) / s,  # 4*qz*qx/(4|qz|) = sig(qz)*qx
				(self.fy + self.uz) / s,  # 4*qy*qz/(4|qz|) = sig(qz)*qy
				s / 4,                      # |qz|
			)
	
	def copy(self):
		return Transform(
			self.rx, self.ry, self.rz,
			self.ux, self.uy, self.uz,
			self.fx, self.fy, self.fz,
			self.px, self.py, self.pz,
		)
	
	def rotate(self, q):
		rx = (
			  self.rx * (q.w*q.w + q.x*q.x - q.y*q.y - q.z*q.z)
			+ self.ry * (q.y*q.x + q.w*q.z)*2
			+ self.rz * (q.z*q.x - q.w*q.y)*2
		)
		ry = (
			  self.rx * (q.x*q.y - q.w*q.z)*2
			+ self.ry * (q.w*q.w + q.y*q.y - q.z*q.z - q.x*q.x)
			+ self.rz * (q.z*q.y + q.w*q.x)*2
		)
		rz = (
			  self.rx * (q.x*q.z + q.w*q.y)*2
			+ self.ry * (q.y*q.z - q.w*q.x)*2
			+ self.rz * (q.w*q.w + q.z*q.z - q.x*q.x - q.y*q.y)
		)
		
		ux = (
			  self.ux * (q.w*q.w + q.x*q.x - q.y*q.y - q.z*q.z)
			+ self.uy * (q.y*q.x + q.w*q.z)*2
			+ self.uz * (q.z*q.x - q.w*q.y)*2
		)
		uy = (
			  self.ux * (q.x*q.y - q.w*q.z)*2
			+ self.uy * (q.w*q.w + q.y*q.y - q.z*q.z - q.x*q.x)
			+ self.uz * (q.z*q.y + q.w*q.x)*2
		)
		uz = (
			  self.ux * (q.x*q.z + q.w*q.y)*2
			+ self.uy * (q.y*q.z - q.w*q.x)*2
			+ self.uz * (q.w*q.w + q.z*q.z - q.x*q.x - q.y*q.y)
		)
		fx = (
			  self.fx * (q.w*q.w + q.x*q.x - q.y*q.y - q.z*q.z)
			+ self.fy * (q.y*q.x + q.w*q.z)*2
			+ self.fz * (q.z*q.x - q.w*q.y)*2
		)
		fy = (
			  self.fx * (q.x*q.y - q.w*q.z)*2
			+ self.fy * (q.w*q.w + q.y*q.y - q.z*q.z - q.x*q.x)
			+ self.fz * (q.z*q.y + q.w*q.x)*2
		)
		fz = (
			  self.fx * (q.x*q.z + q.w*q.y)*2
			+ self.fy * (q.y*q.z - q.w*q.x)*2
			+ self.fz * (q.w*q.w + q.z*q.z - q.x*q.x - q.y*q.y)
		)
		
		px = (
			  self.px * (q.w*q.w + q.x*q.x - q.y*q.y - q.z*q.z)
			+ self.py * (q.y*q.x + q.w*q.z)*2
			+ self.pz * (q.z*q.x - q.w*q.y)*2
		)
		py = (
			  self.px * (q.x*q.y - q.w*q.z)*2
			+ self.py * (q.w*q.w + q.y*q.y - q.z*q.z - q.x*q.x)
			+ self.pz * (q.z*q.y + q.w*q.x)*2
		)
		pz = (
			  self.px * (q.x*q.z + q.w*q.y)*2
			+ self.py * (q.y*q.z - q.w*q.x)*2
			+ self.pz * (q.w*q.w + q.z*q.z - q.x*q.x - q.y*q.y)
		)
		
		self.rx = rx
		self.ry = ry
		self.rz = rz
		self.ux = ux
		self.uy = uy
		self.uz = uz
		self.fx = fx
		self.fy = fy
		self.fz = fz
		self.px = px
		self.py = py
		self.pz = pz
		return self
	
	def antirotate(self, q):
		squag2 = q.squag()**2
		w = q.w / squag2
		x = -q.x / squag2
		y = -q.y / squag2
		z = -q.z / squag2
		rx = (
			  self.rx * (w*w + x*x - y*y - z*z)
			+ self.ry * (y*x + w*z)*2
			+ self.rz * (z*x - w*y)*2
		)
		ry = (
			  self.rx * (x*y - w*z)*2
			+ self.ry * (w*w + y*y - z*z - x*x)
			+ self.rz * (z*y + w*x)*2
		)
		rz = (
			  self.rx * (x*z + w*y)*2
			+ self.ry * (y*z - w*x)*2
			+ self.rz * (w*w + z*z - x*x - y*y)
		)
		
		ux = (
			  self.ux * (w*w + x*x - y*y - z*z)
			+ self.uy * (y*x + w*z)*2
			+ self.uz * (z*x - w*y)*2
		)
		uy = (
			  self.ux * (x*y - w*z)*2
			+ self.uy * (w*w + y*y - z*z - x*x)
			+ self.uz * (z*y + w*x)*2
		)
		uz = (
			  self.ux * (x*z + w*y)*2
			+ self.uy * (y*z - w*x)*2
			+ self.uz * (w*w + z*z - x*x - y*y)
		)
		fx = (
			  self.fx * (w*w + x*x - y*y - z*z)
			+ self.fy * (y*x + w*z)*2
			+ self.fz * (z*x - w*y)*2
		)
		fy = (
			  self.fx * (x*y - w*z)*2
			+ self.fy * (w*w + y*y - z*z - x*x)
			+ self.fz * (z*y + w*x)*2
		)
		fz = (
			  self.fx * (x*z + w*y)*2
			+ self.fy * (y*z - w*x)*2
			+ self.fz * (w*w + z*z - x*x - y*y)
		)
		
		px = (
			  self.px * (w*w + x*x - y*y - z*z)
			+ self.py * (y*x + w*z)*2
			+ self.pz * (z*x - w*y)*2
		)
		py = (
			  self.px * (x*y - w*z)*2
			+ self.py * (w*w + y*y - z*z - x*x)
			+ self.pz * (z*y + w*x)*2
		)
		pz = (
			  self.px * (x*z + w*y)*2
			+ self.py * (y*z - w*x)*2
			+ self.pz * (w*w + z*z - x*x - y*y)
		)
		
		self.rx = rx
		self.ry = ry
		self.rz = rz
		self.ux = ux
		self.uy = uy
		self.uz = uz
		self.fx = fx
		self.fy = fy
		self.fz = fz
		self.px = px
		self.py = py
		self.pz = pz
		return self
	
	def translate(self, v):
		self.px += v.x
		self.py += v.y
		self.pz += v.z
		return self
	
	def antitranslate(self, v):
		self.px -= v.x
		self.py -= v.y
		self.pz -= v.z
		return self
	
	def transform(self, other):
		rx=other.rx*self.rx + other.ux*self.ry + other.fx*self.rz
		ry=other.ry*self.rx + other.uy*self.ry + other.fy*self.rz
		rz=other.rz*self.rx + other.uz*self.ry + other.fz*self.rz
		
		ux=other.rx*self.ux + other.ux*self.uy + other.fx*self.uz
		uy=other.ry*self.ux + other.uy*self.uy + other.fy*self.uz
		uz=other.rz*self.ux + other.uz*self.uy + other.fz*self.uz
		
		fx=other.rx*self.fx + other.ux*self.fy + other.fx*self.fz
		fy=other.ry*self.fx + other.uy*self.fy + other.fy*self.fz
		fz=other.rz*self.fx + other.uz*self.fy + other.fz*self.fz
		
		px=other.rx*self.px + other.ux*self.py + other.fx*self.pz + other.px
		py=other.ry*self.px + other.uy*self.py + other.fy*self.pz + other.py
		pz=other.rz*self.px + other.uz*self.py + other.fz*self.pz + other.pz
		
		self.rx = rx
		self.ry = ry
		self.rz = rz
		self.ux = ux
		self.uy = uy
		self.uz = uz
		self.fx = fx
		self.fy = fy
		self.fz = fz
		self.px = px
		self.py = py
		self.pz = pz
		return self
	
	def pretransform(self, other):
		rx=self.rx*other.rx + self.ux*other.ry + self.fx*other.rz
		ry=self.ry*other.rx + self.uy*other.ry + self.fy*other.rz
		rz=self.rz*other.rx + self.uz*other.ry + self.fz*other.rz
		
		ux=self.rx*other.ux + self.ux*other.uy + self.fx*other.uz
		uy=self.ry*other.ux + self.uy*other.uy + self.fy*other.uz
		uz=self.rz*other.ux + self.uz*other.uy + self.fz*other.uz
		
		fx=self.rx*other.fx + self.ux*other.fy + self.fx*other.fz
		fy=self.ry*other.fx + self.uy*other.fy + self.fy*other.fz
		fz=self.rz*other.fx + self.uz*other.fy + self.fz*other.fz
		
		px=self.rx*other.px + self.ux*other.py + self.fx*other.pz + self.px
		py=self.ry*other.px + self.uy*other.py + self.fy*other.pz + self.py
		pz=self.rz*other.px + self.uz*other.py + self.fz*other.pz + self.pz
		
		self.rx = rx
		self.ry = ry
		self.rz = rz
		self.ux = ux
		self.uy = uy
		self.uz = uz
		self.fx = fx
		self.fy = fy
		self.fz = fz
		self.px = px
		self.py = py
		self.pz = pz
		return self
	
	def transformed(self, other):
		return other @ self
	
	def pretransformed(self, other):
		return self @ other
	
	
	def __eq__(self, other):
		return (
			self.rx == other.rx
			and self.ry == other.ry
			and self.rz == other.rz
			and self.ux == other.ux
			and self.uy == other.uy
			and self.uz == other.uz
			and self.fx == other.fx
			and self.fy == other.fy
			and self.fz == other.fz
			and self.px == other.px
			and self.py == other.py
			and self.pz == other.pz
		)
	
	def __repr__(self):
		return f"Transform(rx:{self.rx}, ry:{self.ry}, rz:{self.rz}, ux:{self.ux}, uy:{self.uy}, uz:{self.uz}, fx:{self.fx}, fy:{self.fy}, fz:{self.fz}, px:{self.px}, py:{self.py}, pz:{self.pz})"
	
	def __str__(self):
		return f"[{self.rx}, {self.ry}, {self.rz}, {self.ux}, {self.uy}, {self.uz}, {self.fx}, {self.fy}, {self.fz}, {self.px}, {self.py}, {self.pz}]"

