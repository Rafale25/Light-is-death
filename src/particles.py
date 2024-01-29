from pyglet.math import Vec2
from random import uniform
from utils import random_uniform_vec2

class Particle:
    def __init__(self, x, y):
        self.pos = Vec2(x, y)
        self.vel = random_uniform_vec2() * 0.5
        self.lifetime = uniform(0.8, 1.2) #seconds

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y

    def is_dead(self):
        return self.lifetime <= 0.0

    def update(self, delta_time):
        self.pos += self.vel * self.lifetime
        self.lifetime -= delta_time

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn(self, x, y):
        self.particles.append(Particle(x, y))

    def update(self, delta_time):
        ## remove dead particles
        self.particles[:] = (x for x in self.particles if not x.is_dead())

        for p in self.particles:
            p.update(delta_time)
