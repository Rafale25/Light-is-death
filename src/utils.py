import glm
from math import sqrt
from random import uniform

def toMatrix(x, y, angle=0, scale=1):
    m = glm.mat4(1.0)
    m = glm.translate(m, glm.vec3(x, y, 0))
    m = glm.rotate(m, angle, glm.vec3(0, 0, 1))
    m = glm.scale(m, glm.vec3(scale))
    return m

def random_uniform_vec2():
    x, y = uniform(-1.0, 1.0), uniform(-1.0, 1.0)
    mag = sqrt(x*x + y*y)
    return glm.vec2(x/mag, y/mag);
