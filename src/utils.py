from pyglet.math import Mat4, Vec2
from math import sqrt, pow
from random import uniform

def toMatrix(x, y, angle=0.0, scale=1.0):
    # return Mat4().scale((scale, scale, 1)).rotate(angle, (0, 0, 1)).translate((x, y, 0))
    return Mat4().translate((x, y, 0)).scale((scale, scale, 1)).rotate(angle, (0, 0, 1)) # No idea why all operations had to be reversed

def random_uniform_vec2():
    v = Vec2(uniform(-1.0, 1.0), uniform(-1.0, 1.0))
    v = v.normalize()
    return v

def map_range(value, min1, max1, min2, max2):
    return min2 + (value - min1) * (max2 - min2) / (max1 - min1);

# def easeInCirc(x):
#     print(x)
#     return 1.0 - sqrt(1.0 - pow(x, 2));

def dump(obj):
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))
