
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




