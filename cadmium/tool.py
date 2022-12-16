from sdf import sdf2,sdf3,SDF2,rectangle,circle
import numpy as np


# define a tool shape in the most minimal way
# "r" the maximum radius of the tool
# "t" radius of the flat bottom of the tool
# "y" height at which the cutting edge merges with the radius
# "m" tool mode, -1 is an external radius cutter, 0 a straight taper, 1 a ball mill
@sdf2
def tool(r : float,t : float,y : float,m : int) -> SDF2 :
    X = np.array((1, 0))
    Y = np.array((0, 1))
    farfaraway = 2**22
    f : SDF2 = rectangle(a=(0,0),b=(r,5))
    if m == 0 :
        # remove "triangle" (more like a very big and very far away circle)
        h = X*(t + (r-t)*.5 ) + Y*y*.5
        d = X*y - Y*(r-t) # normal vector
        dn = np.linalg.norm(d)
        f -= circle(farfaraway,h+(d/dn)*farfaraway)
    if m == 1 :
        # remove negative quadrant
        f -= rectangle(a=(t,0),b=(r,t))
        f |= circle(t,X*t+Y*t)
    if m == -1 :
        # remove positive quadrant
        f -= circle(t,X*r)
    return f

@sdf3
def segment(a, b):
    a = np.array(a)
    b = np.array(b)
    def f(p):
        pa = p - a
        ba = b - a
        h = np.clip(np.dot(pa, ba) / np.dot(ba, ba), 0, 1).reshape((-1, 1))
        return np.linalg.norm(pa - np.multiply(ba, h),axis=1)
    return f

@sdf3
def cut(profile : SDF2,a,b):
    an = np.array((1, 1, 0)) * a
    bn = np.array((1, 1, 0)) * b
    l = capsule(an,bn,0) # distance to projected segment
    def f(p):
        aa = p * np.array((1, 1, 0))
        nn = l(aa)[:,-1] # distance to projected segment
        mm = p[:,-1] # z component
        xy = np.stack([nn,mm],axis=-1)
        dd = profile(xy)
        print(dd.shape)
        return dd[:,0]
    return f