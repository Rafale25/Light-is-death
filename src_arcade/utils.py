from pyglet.math import Mat4#, translate, rotate, scale
from math import sqrt
from random import uniform

def toMatrix(x, y, angle=0, scale=1):
    return Mat4().scale((scale, scale, 1)).rotate(angle, (0, 0, 1)).translate((x, y, 0))

def random_uniform_vec2():
    x, y = uniform(-1.0, 1.0), uniform(-1.0, 1.0)
    mag = sqrt(x*x + y*y)
    return x/mag, y/mag

def map_range(value, min1, max1, min2, max2):
    return min2 + (value - min1) * (max2 - min2) / (max1 - min1);

def dump(obj):
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))
