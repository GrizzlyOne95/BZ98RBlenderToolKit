# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.
def remap_range(a0, b0, a1, b1, n):
	return ((n - a0) * (b1 - a1) / (b0 - a0)) + a1

def remap_range_normal(a, b, n):
	if(a == b):
		return 0
	return (n - a) / (b - a)

def clip(l, m, u):
	if(m < l):
		return l
	if(m > u):
		return u
	return m




